from typing import Any, Awaitable, Callable, List, Optional
import json

from config.supabase_client import supabase
from config.tokenizer import re_rank_chunks
from fastapi import HTTPException
from schemas.ask_schema import AskSupabaseModel
from utils.messages import create_conversation, get_last_messages, save_message
from utils.openai import generate_title_from_question, openai
from utils.supabase_retrieve_chunks import multi_query_retrieve, retrieve_chunks


async def noop_callback(event: str, payload: Any):
    pass


async def process_rag_pipeline(
    body: AskSupabaseModel,
    user_id: str,
    callback: Callable[[str, Any], Awaitable[None]] = noop_callback,
) -> dict:

    # 1. Handle Conversation ID
    if body.conversation_id is None:
        await callback("status", "Creando nueva conversación...")
        title = await generate_title_from_question(body.question)
        conversation = await create_conversation(title, user_id)
        conversation_id = conversation["id"]
    else:
        conversation_id = body.conversation_id

    # 2. Get History
    await callback("status", "Analizando historial...")
    messages = await get_last_messages(conversation_id=conversation_id, user_id=user_id)

    if messages is None:
        context_messages = "No hay historial previo."
    else:
        context_messages = "\n".join(
            [
                f"{message['role'].capitalize()}: {message['content']}"
                for message in messages
            ]
        )

    # 3. Initial Retrieve
    await callback("status", "Buscando documentos relevantes...")
    chunks = retrieve_chunks(
        body.question, body.top_k, body.document_id, filter_user=user_id
    )

    # 4. Generate Variants (if requested)
    if body.variants:
        await callback("status", "Generando variantes de búsqueda...")
        prompt_variants = f"""
          Reformula la siguiente pregunta en 3 formas distintas,
          manteniendo el mismo significado pero con palabras diferentes.
          Pregunta: "{body.question}"
          Devuelve solo una lista JSON de strings estrictamente válida. Ejemplo:
          ["Variante 1", "Variante 2", "Variante 3"]
        """

        try:
            response_variants = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en reformular preguntas para búsqueda semántica.",
                    },
                    {"role": "user", "content": prompt_variants},
                ],
                temperature=0.7,
            )
            variants_content = response_variants.choices[0].message.content
            
            # Limpieza básica para extraer JSON
            clean_content = variants_content.replace("```json", "").replace("```", "").strip()
            variants = json.loads(clean_content)

            if not isinstance(variants, list) or len(variants) == 0:
                raise Exception("Empty variants list")

            # Re-retrieve with variants
            # Recuperamos hasta top_k chunks únicos combinando resultados
            chunks = multi_query_retrieve(
                body.question, variants, body.top_k, body.document_id, user_id
            )[:body.top_k]

        except Exception as e:
            print(f"Error generating variants: {e}")
            # Si falla, continuamos con los chunks originales
            pass

    # 5. Re-rank (if requested)
    if body.re_rank:
        await callback("status", "Re-ordenando resultados...")
        chunks = re_rank_chunks(body.question, chunks)

    # 6. Build Context
    context = "\n\n".join([chunk["content"] for chunk in chunks])

    # 7. Get Document Names (Metadata)
    documents_id = set([chunk["document_id"] for chunk in chunks])
    documents_name = []
    for document_id in documents_id:
        try:
            resp = (
                supabase.table("documents")
                .select("*")
                .eq("id", document_id)
                .eq("user_id", user_id)
                .execute()
            )
            if resp.data:
                documents_name.append(resp.data[0]["name"])
        except Exception as e:
            # Log error but don't fail request
            print(f"Error getting document metadata: {e}")

    await callback("sources", documents_name)

    # 8. Generate Answer
    await callback("status", "Generando respuesta...")

    system_prompt = """
    Eres un asistente de IA experto, analítico y preciso.
    Tu objetivo es responder a las preguntas del usuario basándote PROFUNDAMENTE en el contexto proporcionado y el historial de la conversación.
    
    Directrices:
    1.  Utiliza la información del 'Contexto Recuperado' para fundamentar tu respuesta.
    2.  Si la respuesta está en el contexto, sé detallado y explicativo. Sintetiza la información de múltiples partes si es necesario.
    3.  Si el contexto es parcial, usa lo disponible y menciona qué podría faltar, pero intenta construir una respuesta útil.
    4.  Si el contexto NO es relevante para la pregunta, indícalo claramente.
    5.  Mantén un tono profesional y servicial.
    """

    user_prompt = f"""
    --- HISTORIAL DE CONVERSACIÓN ---
    {context_messages}
    
    --- CONTEXTO RECUPERADO (DOCUMENTOS) ---
    {context}
    
    --- PREGUNTA DEL USUARIO ---
    {body.question}
    
    Por favor, responde a la pregunta anterior utilizando el contexto proporcionado.
    """

    # We use stream=True to support real-time token callback
    stream = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        stream=True,
    )

    full_answer = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_answer += content
            await callback("token", content)

    await callback("done", None)

    # 9. Save Messages
    await save_message(
        message=body.question,
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
    )
    await save_message(
        message=full_answer,
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
    )

    return {
        "question": body.question,
        "answer": full_answer,
        "chunks": chunks,
        "documents": documents_name,
        "conversation_id": conversation_id,
    }
