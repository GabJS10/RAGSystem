import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from typing import List, Dict
from schemas.chunk_schema import Chunk

MODEL_NAME = "BAAI/bge-reranker-v2-m3" 

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Device for reranker:", device)

# Cargar tokenizer y modelo (una sola vez)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

# Si GPU: pasar a half precision y mover al device para acelerar
if device == "cuda":
    model.to(device)
    try:
        model.half()   # fp16
        torch.backends.cudnn.benchmark = True
    except Exception as e:
        print("No se pudo usar half precision:", e)

def re_rank_chunks(query: str, chunks: List[Chunk], top_k: int = 3, max_length: int = 256) -> List[Dict]:
    """
    chunks: lista de dicts con key 'content'
    devuelve lista de (content, score) ordenada desc
    """
    texts = [ch["content"] for ch in chunks]


    # Tokenizar batch (usa padding por defecto -> batch_size)
    inputs = tokenizer(
        [[query, t] for t in texts],
        padding=True,
        truncation=True,
        max_length=max_length,
        return_tensors="pt"
    )

    # Mover tensores al device (muy importante)
    inputs = {k: v.to(device) for k, v in inputs.items()} 

    with torch.inference_mode():
        outputs = model(**inputs)
        scores = outputs.logits.view(-1).float()  # shape: (N,)
    
    # Pasar scores a CPU y emparejar con textos
    scores_cpu = scores.cpu().numpy().tolist()
    ranked = sorted(zip(chunks, scores_cpu), key=lambda x: x[1], reverse=True)[:top_k]

    chunks = [r[0] for r in ranked] 


    #add score

    for i in range(len(chunks)):
        chunks[i]["score"] = ranked[i][1]

    return chunks