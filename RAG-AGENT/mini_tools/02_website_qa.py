import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"

# 2. Scrape and load the website content
url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
loader = WebBaseLoader(url)
docs = loader.load()

# 3. Split website text into manageable chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=60)
chunks = text_splitter.split_documents(docs)

# 4. Create vector embeddings and store in FAISS index
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

# 5. Build Retriever and RAG Chain
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer the question based only on the context provided:\n\n{context}"),
    ("human", "{input}")
])

chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))

# 6. List of 5 questions to ask the website
questions = [
    "What is the definition of Artificial Intelligence?",
    "What are some key milestones or history of AI?",
    "What are the main subfields or applications of AI mentioned?",
    "What risks or ethical concerns are associated with AI?",
    "Who are some prominent researchers or pioneers in the field?"
]

# 7. Loop through and print answers to all 5 questions
for i, q in enumerate(questions, 1):
    result = chain.invoke({"input": q})
    print(f"\n--- Q{i}: {q} ---")
    print(f"A: {result['answer']}")