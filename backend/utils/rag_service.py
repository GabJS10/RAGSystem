from typing import Any, Awaitable, Callable, List, Optional

from config.supabase_client import supabase
from config.tokenizer import re_rank_chunks
from fastapi import HTTPException
from schemas.ask_schema import AskSupabaseModel
from utils.messages import create_conversation, get_last_messages, save_message
from utils.openai import openai
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
        conversation = await create_conversation(body.question, user_id)
        conversation_id = conversation["id"]
    else:
        conversation_id = body.conversation_id

    # 2. Get History
    await callback("status", "Analizando historial...")
    messages = await get_last_messages(conversation_id=conversation_id, user_id=user_id)

    if messages is None:
        context_messages = ""
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
          Devuelve solo una lista JSON de strings. Ejemplo:
          ```json
          ["Variante 1","Variante 2","Variante 3"]
          ```
        """

        try:
            response_variants = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en reformular preguntas.",
                    },
                    {"role": "user", "content": prompt_variants},
                ],
                temperature=0.7,
            )
            variants_content = response_variants.choices[0].message.content
            # Safe eval or json parse could be better, but sticking to original logic for now
            variants = eval(variants_content.split("```")[1].strip().split("json")[-1])

            if not isinstance(variants, list) or len(variants) == 0:
                raise Exception("Empty variants list")

            # Re-retrieve with variants
            chunks = multi_query_retrieve(
                body.question, variants, body.top_k, body.document_id, user_id
            )[:3]

        except Exception as e:
            print(f"Error generating variants: {e}")
            # Fallback to original chunks if variants fail? Or raise?
            # Original code raises HTTPException(500).
            raise HTTPException(status_code=500, detail="Error generating variants")

    # 5. Re-rank (if requested)
    if body.re_rank:
        await callback("status", "Re-ordenando resultados...")

        # modificar re_rank_chunks para que devuelva chunks con document_id
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
            # Original code raises 500 here
            raise HTTPException(
                status_code=500, detail=f"Error getting document from Supabase: {e}"
            )

    await callback("sources", documents_name)

    # 8. Generate Answer
    prompt = f"""
      Context_of_previous_conversation: {context_messages}
      Main_Context: {context}
      Question: {body.question}
      Answer:
    """

    await callback("status", "Generando respuesta...")

    # We use stream=True to support real-time token callback
    # But we also need to accumulate the full answer for the return value/saving.
    stream = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente experto que responde usando únicamente el contexto proporcionado.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
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
        "conversation_id": conversation_id,  # Return this too as it might be new
    }
