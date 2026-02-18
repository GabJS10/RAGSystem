from typing import List, Optional
import re
import hashlib
import tiktoken
from schemas.chunk_schema import Chunk

_enc = tiktoken.get_encoding("cl100k_base")

def normalize_text(txt: str) -> str:
    """Normaliza texto para hashing y conteo de tokens"""
    return re.sub(r"\s+", " ", txt.strip())

def count_tokens(text: str) -> int:
    return len(_enc.encode(normalize_text(text)))

def sha256(txt: str) -> str:
    return hashlib.sha256(normalize_text(txt).encode("utf-8")).hexdigest()

def recursive_split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Divide el texto recursivamente usando separadores para mantener la estructura semántica.
    Prioridad: Párrafos -> Líneas -> Oraciones -> Palabras
    """
    separators = ["\n\n", "\n", ". ", " ", ""]
    
    def _split(text: str, seps: List[str]) -> List[str]:
        if not seps:
            # Fallback: hard split
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]
            
        sep = seps[0]
        if sep == "":
             return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size-overlap)]

        # Dividir manteniendo el separador
        pattern = f"({re.escape(sep)})"
        parts = re.split(pattern, text)
        
        final_parts = []
        for part in parts:
            if not part: continue
            if len(part) > chunk_size:
                final_parts.extend(_split(part, seps[1:]))
            else:
                final_parts.append(part)
        return final_parts

    atoms = _split(text, separators)
    
    chunks = []
    current_chunk = []
    current_len = 0
    
    for atom in atoms:
        atom_len = len(atom)
        
        if current_len + atom_len > chunk_size:
            if current_chunk:
                chunks.append("".join(current_chunk))
            
            # Overlap: mantener últimos átomos
            overlap_len = 0
            new_chunk = []
            for item in reversed(current_chunk):
                if overlap_len + len(item) <= overlap:
                    new_chunk.insert(0, item)
                    overlap_len += len(item)
                else:
                    break
            
            current_chunk = new_chunk + [atom]
            current_len = overlap_len + atom_len
        else:
            current_chunk.append(atom)
            current_len += atom_len
            
    if current_chunk:
        chunks.append("".join(current_chunk))
        
    return chunks

def chunk_text(text: str, page_num: int, chunk_size: int = 1000, overlap: int = 200) -> List[Chunk]:
    """
    Genera chunks a partir de un texto.
    """
    text_chunks = recursive_split_text(text, chunk_size, overlap)
    
    result_chunks: List[Chunk] = []
    for chunk_content in text_chunks:
        content_stripped = chunk_content.strip()
        if content_stripped:
            result_chunks.append({
                "content": content_stripped,
                "chunk_index": -1, 
                "token_count": count_tokens(content_stripped),
                "page": page_num,
                "document_id": "" 
            })
            
    return result_chunks

def build_chunks_for_document(pages_text: List[str], chunk_size: int = 1000, overlap: int = 200) -> List[Chunk]:
    all_chunks = []
    prev_overlap = ""
    
    for page_num, page_text in enumerate(pages_text, start=1):
        # Concatenar overlap anterior
        if prev_overlap:
            full_text = prev_overlap + " " + page_text
        else:
            full_text = page_text
            
        page_chunks = chunk_text(full_text, page_num, chunk_size, overlap)
        all_chunks.extend(page_chunks)
        
        # Guardar overlap para siguiente página
        if len(page_text) > overlap:
            prev_overlap = page_text[-overlap:]
        else:
            prev_overlap = page_text

    for i, ch in enumerate(all_chunks):
        ch["chunk_index"] = i
        
    return all_chunks
