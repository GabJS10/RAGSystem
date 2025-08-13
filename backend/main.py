from fastapi import FastAPI, UploadFile, HTTPException, File
from utils.extractor import extract_text_from_file
from utils.chuncker import chunk_text
from utils.embedder import get_embedding
from utils.vector_store import VectorStore
from schemas.ask_schema import AskModel
from utils.openai import openai
#Initialize the vector store
vector_store = VectorStore()

#Inicialize the FastAPI app
app = FastAPI()

#Endpoint to extract text
@app.post("/extract_text")
#is async because we are reading the file content
#file argument its a UploadFile object because that allows us to send
#files to the endpoint, set the default value to File(...)
async def extract_text(file: UploadFile = File(...)):
  #Check the file type if its not pdf or docx raise an error
  if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"]:
    raise HTTPException(status_code=400, detail="Invalid file type")

  #Read the file content
  content = await file.read()
  #Extract the text
  text = extract_text_from_file(file.filename, content)
  #Return the text
  #Split the text into chunks
  chunks = chunk_text(text)



  for idx, chunk in enumerate(chunks):
    embedding = get_embedding(chunk)
    vector_store.add(embedding, chunk, {"id": idx, "filename": file.filename})


  return {"text": text[:200],"chunks": chunks,"vectorized":True}


@app.post("/ask")
async def ask(data: AskModel):
  embedding = get_embedding(data.question)
  results = vector_store.search(embedding, data.top_k)
  
  if not results:
    raise HTTPException(status_code=404, detail="No results found")
  
  context = "\n\n".join([result["text"] for result in results])
  
  prompt = f"""
  Context: {context}
  Question: {data.question}
  Answer:
  """

  response = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "system", "content": "Eres un asistente experto que responde usando únicamente el contexto proporcionado."}
      ,{"role": "user", "content": prompt}]
  )

  answer = response.choices[0].message.content


  return {"question": data.question, "answer": answer,"chunks":[result["metadata"] for result in results]}