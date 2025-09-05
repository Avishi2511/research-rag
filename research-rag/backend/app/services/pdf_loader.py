import fitz  # PyMuPDF
from typing import List, Dict
import os

class PDFLoader:
    def __init__(self):
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF page by page
        Returns: List of {page_number, text, source_file}
        """
        doc = fitz.open(pdf_path)
        pages_data = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            if text.strip():  # Only add pages with content
                pages_data.append({
                    "page_number": page_num + 1,
                    "text": text,
                    "source_file": os.path.basename(pdf_path)
                })
        
        doc.close()
        return pages_data
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict]:
        """Process multiple PDFs and return combined page data"""
        all_pages = []
        
        for pdf_path in pdf_paths:
            try:
                pages = self.extract_text_from_pdf(pdf_path)
                all_pages.extend(pages)
            except Exception as e:
                print(f"Error processing {pdf_path}: {str(e)}")
                continue
                
        return all_pages
