from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

persistent_directory = "db/chroma_db"

#Load embeddings and vector store

embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)

# Search for relevant document

query = "In what did telsa started the production of the raodstar"

retriever = db.as_retriever(search_kwargs={"k":5})

relevant_docs=retriever.invoke(query)

print(f"User query: {query}")

#Display results

print("--- Context ---")
for i, doc in enumerate(relevant_docs):
    print(f"Document {i}:\n{doc.page_content}")

combined_input = f"""Based on the following documents, please answer this question:{query}

Documents

{ relevant_docs}

Please provide a clear, helpful answer using only the informations from these documents. if you can't find the answer in the document say you donot have enough context, don't anwser base on your knowledge

"""

model = ChatOpenAI(model="gpt-4o")

message = [
    SystemMessage(content="You are A helpful Assistant"),
    HumanMessage(content=combined_input)
]

result = model.invoke(message)

print("\n ---- Generated Response-----")

print("Content Only")
print(result.content)