from typing import List

#This function splits the text into chunks

#Parameters: text. chunk_size and overlap and return a list (chunks)
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    chunks = []
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
            chunks.append(chunk)
        
        start += chunk_size - overlap  # Move to the next chunk

    return chunks
