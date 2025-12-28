import fitz
import tempfile, os
import re
from typing import List
from spire.doc import Document 
from spire.doc import FixedLayoutDocument
from spire.doc import FileFormat, HeaderFooterType
def extract_text_from_file(filename: str, content: bytes) -> List[str]:
    
    #Check the file type
    if filename.endswith(".pdf"):
        return extract_pdf_pages(content)
    elif filename.endswith(".docx"):
        return extract_docx_paragraphs(content)
    #If the file type is not pdf or docx
    #Return an empty string
    elif filename.endswith(".txt"):
        return content.decode("utf-8")
    else:
        return ""

# ---- Implementación DOCX
def extract_docx_paragraphs(content: bytes) -> List[str]:
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(content)
        tmp_path = tmp.name 
    
    doc = Document()
    doc.LoadFromFile(tmp_path)


    # delete footers of the document
    section = doc.Sections[0]

    # Iterate through all paragraphs in the section
    for i in range(section.Paragraphs.Count):
        para = section.Paragraphs.get_Item(i)

        # Iterate through all child objects in each paragraph
        for j in range(para.ChildObjects.Count):
            obj = para.ChildObjects.get_Item(j)

            # Delete footer in the first page
            footer = None
            footer = section.HeadersFooters[HeaderFooterType.FooterFirstPage]
            if footer is not None:
                footer.ChildObjects.Clear()

            # Delete footers in the odd pages
            footer = section.HeadersFooters[HeaderFooterType.FooterOdd]
            if footer is not None:
                footer.ChildObjects.Clear()

            # Delete footers in the even pages
            footer = section.HeadersFooters[HeaderFooterType.FooterEven]
            if footer is not None:
                footer.ChildObjects.Clear()

    layoutDoc = FixedLayoutDocument(doc)
    pages = []
    for i in range(layoutDoc.Pages.Count):
        page = layoutDoc.Pages.get_Item(i)

        if page is not None:
            text = page.Text.strip()
            pages.append(clean_text(text))
    
    doc.Close()
    os.remove(tmp_path)
    return pages


def extract_pdf_pages(content: bytes) -> List[str]:
    pages = []
    with fitz.open(stream=content, filetype="pdf") as doc:
        for p in doc:
            pages.append(p.get_text("text"))
    return pages


def clean_text(text: str) -> str:
    # Reemplazar símbolos extraños
    text = re.sub(r'[¶¤]', '', text)
    # Quitar dobles espacios
    text = re.sub(r'\s+', ' ', text)
    return text.strip()