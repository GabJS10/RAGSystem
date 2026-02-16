import os

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

client = openai.AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def generate_title_from_question(question: str) -> str:
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Genera un corto y conciso título (máximo 5 palabras) para una conversación basado en la pregunta del usuario.",
                },
                {"role": "user", "content": question},
            ],
            max_tokens=20,
        )
        content = response.choices[0].message.content
        title = content.strip() if content else "Nueva conversación"
        return title
    except Exception as e:
        print(f"Error generating title: {e}")
        return "Nueva conversación"
