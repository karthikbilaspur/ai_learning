import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Set your OpenAI API key for generation
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Load the PDF file
pdf_path = "sample.pdf"  # Ensure this PDF exists in the same directory
loader = PyPDFLoader(pdf_path)
docs = loader.load()

# 3. Split the PDF text into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

# 4. Create local vector embeddings & store them in FAISS
print("Embedding documents... (running locally)")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 5. Set up the Retriever & LLM
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 6. Build the RAG Prompt & Chain
system_prompt = (
    "You are a helpful assistant. Use the following context to answer the question.\n"
    "If you don't know, say you don't know.\n\n"
    "Context:\n{context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 7. Ask a question
query = "What is the main summary of this document?"
response = rag_chain.invoke({"input": query})

print("\n--- Answer ---")
print(response["answer"])