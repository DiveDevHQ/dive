from io import BytesIO
import pypdf
import requests
from abc import abstractmethod
from typing import Callable, Dict, Generator, List, Optional, Type, Any


class BaseReader:
    """Utilities for loading data from a directory."""

    @abstractmethod
    def load_data(self, *args: Any, **load_kwargs: Any) -> List[Any]:
        """Load data from the input directory."""


class PDFReader(BaseReader):
    """PDF parser."""
    def load_data(
            self, doc_id, file_name, file_url, extra_info
    ):
        r = requests.get(file_url)
        with BytesIO(r.content) as data:
            docs = []
            read_pdf = pypdf.PdfReader(data)
            part = 0
            for page in range(len(read_pdf.pages)):
                page_text = read_pdf.pages[page].extract_text()
                page_label = read_pdf.page_labels[page]
                metadata = {"page_label": page_label, "file_name": file_name}
                if extra_info is not None:
                    metadata.update(extra_info)
                docs.append({'id': f"{str(doc_id)}_part_{part}", 'data': page_text, 'metadata': metadata})
                part += 1
        return docs


class TxtReader(BaseReader):
    """Txt parser."""
    def load_data(
            self, doc_id, file_name, file_url, extra_info
    ):
        r = requests.get(file_url)
        docs = []
        with BytesIO(r.content) as data:
            metadata = {"file_name": file_name}
            if extra_info is not None:
                metadata.update(extra_info)
            docs.append({'id': f"{str(doc_id)}", 'data': r.text, 'metadata': metadata})
        return docs