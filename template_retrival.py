import json
from typing import List, Dict
from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

def set_chroma_db(templates_list: List[Dict]):
    documents = [
        Document(
            page_content=json.dumps(item, indent=2)
        )
        for item in templates_list
    ]
    model_name = "all-MiniLM-L6-v2"
    embedding_function = HuggingFaceEmbeddings(model_name=model_name)
    chroma_db = Chroma.from_documents(
        documents,  
        embedding_function
    )

    return chroma_db

def get_related_template(chroma_db, jd:str) -> List[Dict]:
    

    results_1 = chroma_db.similarity_search(jd, k=2)
    results_1_json = json.loads(results_1[0].page_content)

    return [results_1_json]

if __name__ == '__main__':

    from data.resume_templates import RESUME_TEMPLATES

    chroma_db=set_chroma_db(RESUME_TEMPLATES)
    payload = get_related_template(chroma_db,"Need a data scientist with experience in Python, SQL, and machine learning.")
    print(json.dumps(payload, indent=2))
