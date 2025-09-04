# pip install langchain langchain-community pypdf

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_and_split(file_path):
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        raise ValueError("Unsupported file type. Use .txt or .pdf")

    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(documents)

    print(f"Total chunks created: {len(docs)}")
    return docs

if __name__ == "__main__":
    chunks = load_and_split("policy.txt")
