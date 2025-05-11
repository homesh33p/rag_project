from app.config import settings
from langchain_core.documents import Document
import csv
import uuid

class CSVParser:

    def __init__(self) -> None:
        pass

    def _load_documents_from_csv(self, csv_path = f"app/embeddings/userguide_v{settings.CSV_VERSION}.csv"):
        """Load documents from CSV file"""
        documents = []
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                content = row.get('content') or row.get('enhancedContent')
                if content:
                    doc = Document(
                        id=uuid.uuid4(),
                        page_content=content,
                        metadata={
                            'headingTrace': row.get('headingTrace', ''),
                            'pageTrace': row.get('pageTrace', ''),
                            'page_id': row.get('page_id', ''),
                            'section_id': row.get('section_id', '')
                        }
                    )
                    documents.append(doc)
        return documents