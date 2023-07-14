#from langchain.schema import Document
from llama_index import Document


def get_documents(documents, extra_metadata):
    transform_documents = []
    for document in documents:
        metadata = document.get('metadata', None)
        if metadata and extra_metadata:
            metadata.update(extra_metadata)
        doc = Document(text=document['text'], metadata=metadata or {})
        doc.id_ = document['id']
        transform_documents.append(doc)
    return transform_documents

'''
    for document in documents:
        metadata = document.get('metadata', None)
        if metadata and extra_metadata:
            metadata.update(extra_metadata)
        doc = Document(page_content=document['text'], metadata=metadata or {})
        doc.id_ = document['id']
        transform_documents.append(doc)
    '''
