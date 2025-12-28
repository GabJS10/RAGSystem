from utils.openai import openai
def get_embedding(text: str | list[str] , model: str = "text-embedding-3-small") -> list[float]:
    if isinstance(text, str):
        text = text.replace("\n", " ")
        text = [text]
    else:
        text = [t.replace("\n", " ") for t in text]
    
    response = openai.embeddings.create(
        input=text,
        model=model
    )
    return [data.embedding for data in response.data]
