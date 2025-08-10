import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# Load env variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY")

# Load your Text file
loader = TextLoader("README.txt")
docs = loader.load()

# Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
print('The total number of Chunks:', len(chunks))

# Use HuggingFace embeddings (free & works locally)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

# Create Groq LLM
llm = ChatGroq(model_name="llama3-8b-8192", groq_api_key=groq_api_key)

# Retrieval QA
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

# Ask a question
query = "What is Large Language Models?"
response = qa_chain.run(query)
print("Answer:", response)
