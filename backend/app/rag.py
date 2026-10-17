from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import json
from app.config import LLM_MODEL


def generate_final_answer(db,user_question,chat_history):
    """Generate final answer using multimodal content"""
    #creating the chat history list
   

  

    try:
        #Initailize LLM (needs vision model for images)
        llm = ChatOpenAI(model=LLM_MODEL, temperature=0)


        if chat_history:
                message = [
                    SystemMessage(content="Given the chat History, rewrite the new question question to be standalon and search")
                ] + chat_history + [
                    HumanMessage(content=f" New question{user_question}")
                ]
                result = llm.invoke(message)
                search_question = result.content.strip()
                print(f"Searching for:{search_question}")
        else:
                search_question = user_question

        #Step 2: Find relevant documents
        retriever = db.as_retriever(search_kwargs={"k":3})
        chunks = retriever.invoke(search_question)

        #build the text prompt

        prompt_text = f"""Based on the following documents, please answer this question: {search_question}

CONTENT TO ANALYZE:"""
        for i, chunk in enumerate(chunks):
            prompt_text += f"--- Document {i+1}---"
            if 'original_content' in chunk.metadata:
                original_data = json.loads(chunk.metadata["original_content"])

                #add raw text
                raw_text = original_data.get("raw_text", "")
                if raw_text:
                    prompt_text += f"Text: \n {raw_text}\n\n"
                table_html = original_data.get("tables_html", [])
                if table_html:
                    prompt_text += f"TABLES: \n"
                    for j, table in enumerate(table_html):
                        prompt_text += f"Table {j+1}: \n {table}"
            prompt_text+="\n"
        prompt_text += """
        Please provide a clear, comprehensive answer using the text, tables, and images above. If the documents don't contain sufficient information to answer the question, say "I don't have enough information to answer that question based on the provided documents."

        ANSWER:"""

        #build all images from all chunks
        message_content =  [{"type":"text", "text":prompt_text}]

        for i, chunk in enumerate(chunks):
            if 'original_content' in chunk.metadata:
                original_data = json.loads(chunk.metadata['original_content'])

                images_base64 = original_data.get('images_base64', [])
                for image_base64 in images_base64:
                    message_content.append({
                        "type":"image_url",
                        "image_url":{"url": f"data:image/jpeg;base64,{image_base64}"}
                    })

        #Send to AI and get response
        message = HumanMessage(content=message_content)
        response = llm.invoke([message])
        chat_history.append(HumanMessage(content=user_question))
        chat_history.append(AIMessage(content=response.content))

        return {
            "answer": response.content,
            "sources": [{"source": c.metadata["source"], "page": c.metadata["page_number"]} for c in chunks],
        }
    except Exception as e:
        print(f"Answer generation failed: {e}")
        return {"answer": "Sorry, I encountered an error while generating the answer.", "sources": []}