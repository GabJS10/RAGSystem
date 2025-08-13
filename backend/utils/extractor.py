import fitz
import docx
import io

#This function is used to extract the text from the file
#Parameters are: filename and content of the file and returns the text
def extract_text_from_file(filename: str, content: bytes) -> str:
    
    #Check the file type
    if filename.endswith(".pdf"):
        return extract_text_from_pdf(content)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(content)
    #If the file type is not pdf or docx
    #Return an empty string
    elif filename.endswith(".txt"):
        return content.decode("utf-8")
    else:
        return ""

def extract_text_from_pdf(content: bytes) -> str:
    text = ""
    with fitz.open(stream=content, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(content: bytes) -> str:
    text = ""
    file_stream = io.BytesIO(content)
    doc = docx.Document(file_stream)
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text