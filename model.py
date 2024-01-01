import streamlit as st
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import sys

def main():
    st.title("Conversational Retrieval System")

    DB_FAISS_PATH = "vectorstore/db_faiss"
    file_path = st.text_input("Enter CSV file path:", "data/heart.csv")
    loader = CSVLoader(file_path=file_path, encoding="utf-8", csv_args={'delimiter': ','})
    data = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(data)

    st.write(f"Total text chunks: {len(text_chunks)}")

    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    docsearch = FAISS.from_documents(text_chunks, embeddings)
    docsearch.save_local(DB_FAISS_PATH)

    llm = CTransformers(model="models/llama-2-7b-chat.ggmlv3.q4_0.bin",
                        model_type="llama",
                        max_new_tokens=512,
                        temperature=0.1)

    qa = ConversationalRetrievalChain.from_llm(llm, retriever=docsearch.as_retriever())

    st.write("Enter your query:")
    query = st.text_input("Input Prompt:")
    if query:
        chat_history = []
        result = qa({"question": query, "chat_history": chat_history})
        st.write("Response:", result['answer'])

if __name__ == "__main__":
    main()
