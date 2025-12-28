from typing import List,Dict
import re
import hashlib
import tiktoken
from utils.openai import openai
from schemas.chunk_schema import Chunk
_enc = tiktoken.get_encoding("cl100k_base")

def normalize_text(txt: str) -> str:
    """Normaliza texto para hashing y conteo de tokens"""
    return re.sub(r"\s+", " ", txt.strip())

def count_tokens(text: str) -> int:
    return len(_enc.encode(normalize_text(text)))

def sha256(txt: str) -> str:
    return hashlib.sha256(normalize_text(txt).encode("utf-8")).hexdigest()

#This function splits the text into chunks

#Parameters: text. chunk_size and overlap and return a list (chunks)
def chunk_text(text: str, page_num: int, chunk_size: int = 300, overlap: int = 60) -> List[Chunk]:
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")

    chunks: List[Chunk] = []
    start = 0
    text_length = len(text)

    # This loop operates until the end of the text
    #inicialize start with 0 and text_length with the length of the text
    while start < text_length:
        
        # Calculate the end of the chunk
        #While the start is less than the length of the text 
        #When the text_length is less means that the end is the end of the text
        end = min(start + chunk_size, text_length)
        
        #Let's go through part of the text and remove the spaces
        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "content": chunk,
                "chunk_index": -1,  # Will be set later
                "token_count": count_tokens(chunk),
                "page": page_num
            })
        
        start += chunk_size - overlap  # Move to the next chunk

    return chunks


def build_chunks_for_document(pages_text: List[str], chunk_size: int = 500, overlap: int = 100) -> List[Chunk]:
    all_chunks = []
    last_page_text = ""
    for page_num, page_text in enumerate(pages_text, start=1):
        if last_page_text:
            combined_text = last_page_text + " " + page_text[:overlap]
            all_chunks.append({
                "content": normalize_text(combined_text),
                "chunk_index": -1,  # Will be set later
                "token_count": count_tokens(combined_text),
                "page": page_num,
            })

        page_chunks = chunk_text(page_text, page_num, chunk_size, overlap)
        all_chunks.extend(page_chunks)

        last_page_text = page_text[-overlap:]  # Save the last part for the next page



    for i, ch in enumerate(all_chunks):
        ch["chunk_index"] = i
    return all_chunks


