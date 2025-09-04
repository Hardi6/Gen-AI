# pip install langchain openai faiss-cpu tiktoken

import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# -----------------------
# Step 1: Set your OpenAI API key
# (or use $env:OPENAI_API_KEY="sk-..." in PowerShell)
os.environ["OPENAI_API_KEY"] = "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"

# -----------------------
# Step 2: Sample policy document (you can replace this with a file)
policy_text = """
Company Refund Policy:
We offer a full refund within 30 days of purchase if you are not satisfied 
with our product. After 30 days, refunds will not be processed. 
To request a refund, please contact our support team with proof of purchase.
"""

# Save to a text file for loading
with open("policy.txt", "w") as f:
    f.write(policy_text)

# -----------------------
# Step 3: Load and split document
loader = TextLoader("policy.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = splitter.split_documents(documents)

# -----------------------
# Step 4: Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(docs, embeddings)

# -----------------------
# Step 5: Build RetrievalQA chain
llm = ChatOpenAI(model="gpt-3.5-turbo")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    chain_type="stuff"
)

# -----------------------
# Step 6: Ask a question
query = "What is the refund policy?"
answer = qa.run(query)

print("Q:", query)
print("A:", answer)
