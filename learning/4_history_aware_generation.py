from langchain_chroma import Chroma
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

persistent_directory = "db/chroma_db"
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

db = Chroma(persist_directory=persistent_directory,embedding_function=embedding_model)

model = ChatOpenAI(model="gpt-4o")

chat_history = []

def ask_question(user_question):

    print(f"\n--- You ask : {user_question}---")

    #Step 1: Make the question clear using conversation history
    if chat_history:
        message = [
            SystemMessage(content="Given the chat History, rewrite the new question question to be standalon and search")
        ] + chat_history + [
            HumanMessage(content=f" New question{user_question}")
        ]

        result = model.invoke(message)
        search_question = result.content.strip()
        print(f"Searching for:{search_question}")
    else:
        search_question = user_question

    #Step 2: Find relevant documents
    retriever = db.as_retriever(search_kwargs={"k":3})
    docs = retriever.invoke(search_question)

    print(f"Found {len(docs)} relevant documents")

    for i, doc in enumerate(docs):
        
        print(f" Doc {i}: {doc.page_content}....")

    combined_input = f"""Based on the following documents, please answer this question:{user_question}

    Documents

    {docs}

    Please provide a clear, helpful answer using only the informations from these documents. if you can't find the answer in the document say you donot have enough context, don't anwser base on your knowledge

    """
    message = [
               SystemMessage(content="You are a helpful assistant that answers qustion based on the provided documents and converstion history")
           ] + chat_history + [
               HumanMessage(content=combined_input)
           ]
    ans = model.invoke(message)
    ans_r = ans.content

    chat_history.append(HumanMessage(content=user_question))
    chat_history.append(AIMessage(content=ans_r))
    return ans_r

    #simple chat loop
def start_chat():
    print("Ask me any question!! type quit to exit")

    while True:
        question = input("\n Your question :")
        if question.lower() == 'quit':
            print("GoodBye")
            break
        ans_r=ask_question(question)
        print(f"Model reponse: {ans_r}")

if __name__ == "__main__":
    start_chat()