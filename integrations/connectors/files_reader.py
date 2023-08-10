from io import BytesIO
import pypdf
import requests
import docx2txt
from abc import abstractmethod
from typing import Callable, Dict, Generator, List, Optional, Type, Any
import environ
env = environ.Env()
environ.Env.read_env()
import os
import json
import base64


class BaseReader:
    """Utilities for loading data from a directory."""

    @abstractmethod
    def load_data(self, *args: Any, **load_kwargs: Any) -> List[Any]:
        """Load data from the input directory."""

    @abstractmethod
    def load_data_from_url(self, *args: Any, **load_kwargs: Any) -> List[Any]:
        """Load data from the input directory."""


class PDFReader(BaseReader):
    """PDF parser."""

    def load_data_from_url(
            self, doc_id, file_name, file_url, extra_info,private
    ):
        r = get_file_data(file_url,private)
        with BytesIO(r) as data:
            docs = []
            read_pdf = pypdf.PdfReader(data)
            part = 0
            for page in range(len(read_pdf.pages)):
                page_text = read_pdf.pages[page].extract_text()
                page_label = read_pdf.page_labels[page]
                metadata = {"page_label": page_label, "file_name": file_name, "page_number": part}
                if extra_info is not None:
                    metadata.update(extra_info)
                docs.append({'id': f"{str(doc_id)}_part_{part}", 'data': page_text, 'metadata': metadata})
                part += 1
        return docs


class PDFVisualReader(BaseReader):
    """PDF OCR parser."""

    def load_data_from_url(
            self, doc_id, file_name, file_url, extra_info,private
    ):
        '''
        OCR_API_KEY = env.str('OCR_API_KEY', default='') or os.environ.get('OCR_API_KEY', '')
        headers = {
            'apikey': OCR_API_KEY,
        }
        r = get_file_data(file_url,private)
        encoded_string = 'data:application/pdf;base64,'+base64.b64encode(r).decode("utf-8")
        print(encoded_string[0:100])
        body={'language':'eng', 'filetype':'pdf','base64Image': encoded_string}
        r = requests.post("https://api.ocr.space/parse/image", data=body, headers=headers)
        print(r)
        '''

        import pytesseract
        from pdf2image import convert_from_bytes

        r = get_file_data(file_url,private)
        docs = []
        doc = convert_from_bytes(r)

        part = 0
        for page_number, page_data in enumerate(doc):
            result = pytesseract.image_to_string(page_data).encode("utf-8")
            metadata = {"file_name": file_name, "page_number": part}
            if extra_info is not None:
                metadata.update(extra_info)
            docs.append({'id': f"{str(doc_id)}_part_{part}", 'data': result.decode("utf-8"), 'metadata': metadata})
            part += 1

        return docs



class TxtReader(BaseReader):
    """Txt parser."""

    def load_data_from_url(
            self, doc_id, file_name, file_url, extra_info,private
    ):
        r = get_file_data(file_url,private)
        docs = []
        with BytesIO(r) as data:
            metadata = {"file_name": file_name}
            if extra_info is not None:
                metadata.update(extra_info)
            docs.append({'id': f"{str(doc_id)}", 'data': r.text, 'metadata': metadata})
        return docs


class DocxReader(BaseReader):
    """Docx parser."""

    def load_data_from_url(
            self, doc_id, file_name, file_url, extra_info,private
    ):
        """Parse file."""
        r = get_file_data(file_url,private)
        docs = []
        with BytesIO(r) as data:
            text = docx2txt.process(data)
            metadata = {"file_name": file_name}
            if extra_info is not None:
                metadata.update(extra_info)
            docs.append({'id': f"{str(doc_id)}", 'data': text, 'metadata': metadata})
        return docs


def get_file_data(file_url, private):
    import boto3

    if private:
        AWS_S3_BUCKET_NAME = env.str('AWS_S3_BUCKET_NAME', default='') or os.environ.get('AWS_S3_BUCKET_NAME', '')
        AWS_ADMIN_ACCESS_KEY = env.str('AWS_ADMIN_ACCESS_KEY', default='') or os.environ.get('AWS_ADMIN_ACCESS_KEY', '')
        AWS_ADMIN_SECRET_KEY = env.str('AWS_ADMIN_SECRET_KEY', default='') or os.environ.get('AWS_ADMIN_SECRET_KEY', '')
        AWS_S3_BUCKET_REGION = env.str('AWS_S3_BUCKET_REGION', default='') or os.environ.get('AWS_S3_BUCKET_REGION', '')
        s3 = boto3.resource('s3',aws_access_key_id=AWS_ADMIN_ACCESS_KEY,
                            aws_secret_access_key=AWS_ADMIN_SECRET_KEY,
                            region_name=AWS_S3_BUCKET_REGION)
        obj = s3.Object(AWS_S3_BUCKET_NAME, file_url)
        return obj.get()['Body'].read()
    else:
        return requests.get(file_url).content