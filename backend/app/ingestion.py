#the partion method the first method to partion our pdf into atomic element
from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title

from app.config import CHROMA_DIR, EMBEDDING_MODEL, LLM_MODEL, DATABASE_URL, COLLECTION_NAME

#Langchain component
from typing import List
import json
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.messages import  HumanMessage

from langchain_postgres import PGVector
from dotenv import  load_dotenv

load_dotenv()
def partition_document(file_path:str):
    """"Extract Element from the PDF using Unstrcutured"""

    print(f"Partitioning Document.... {file_path}")

    element = partition_pdf(
            filename=file_path, #our Pdf file path
            strategy="hi_res", # use most accurate (but slower) processing method of extraction
            infer_table_structure=True, #keep Table as structured Html, not jambed text
            extract_image_block_types=['Image'], # Grab images found in the pdf
            extract_image_block_to_payload=True # store images as based64 data that u can actively use
    ) 
    print(f"Extracted {len(element)} elments")
    return element


#chunking by title

def create_chunk_by_title(elements):
    """Create intelligent chunks title title-baded"""
    print("Creating Smart Chunks....")

    chunks = chunk_by_title(
        elements,
        max_characters=3000, #Hard limit, this limit is never exceeded
        new_after_n_chars=2400, #Try to start a new chunk after 2400 x-ters
        combine_text_under_n_chars=500 #combine  tiny chunks under 500 chars with neightbours
    )

    print(f"Created {len(chunks)} chunks")
    return chunks

#Separating content by type

def separate_content_types(chunk):
    """Analyse what type of content are in the chunk"""

    content_data = {
        'text':chunk.text,
        'tables':[],
        'images':[],
        'types' :['text']
    }

    #check for table and images in the original elements

    if hasattr(chunk,'metadata') and hasattr(chunk.metadata, 'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__


            #Handle tables
            if element_type == 'Table':
                content_data['types'].append('table')
                table_html = getattr(element.metadata, 'text_as_html', element.text)
                content_data['tables'].append(table_html)

            #handle images

            elif element_type == 'Image':
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                    content_data['types'].append('image')
                    content_data['images'].append(element.metadata.image_base64)


    content_data['types'] = list(set(content_data['types']))
    return content_data


def create_ai_enhanced_summary(text:str,tables:List[str], images:List[str])->str:
    """Create AI-enhanced sumary for mixed content"""

    try:
        #Initialise LLM (need vision model for images)

        llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

        #Build the context prompt

        prompt_text = f""" You are Creating a searchable description for document content retrieval

        CONTEXT TO ANALYSE:
        TEXT CONTENT/
        {text}
            \n\n
        """
        prompt_text +=""" Your Task :
                               Generate a comprehensive, searchable description that covers:
                               1.key facts, numbers, and data points from text and table
                               2.Main topics and concepts discoused
                               3.questions this content could answer
                               4.visual content analysis(charts, diagrams, patterns in images)
                               5.Alternative search terms users might use
               
                               make it detailed and searchable - findability over bravity.
               
                               Searchable Description description: \n\n
                                 """

        #add tables if present
        if tables:
            prompt_text += "TABLE\n"
            for i, table in enumerate(tables):
                prompt_text += f"Table {i+1}:\n {table}"

        #build message content starting with text
        message_content = [{"type":"text", "text":prompt_text}]

        #add images to the message

        for image_base64 in images:

            message_content.append({"type":"image_url",
                                    "image_url":{"url": f"data:image/jpeg;base64,{image_base64}"}}) 

            #Send to AI and get response
        message = HumanMessage(content=message_content)
        reponse = llm.invoke([message])
        return reponse.content
    except Exception as e:
        print(f"AI Samary failed: {e}")
        #Fallback to simple sumary
        sumary = f"{text[:300]}..."
        if tables:
            sumary += f"[Contains {len(tables)} tales(s)]"
        if images:
            sumary += f"[Contains {len(images)} images(s)]"
        return sumary


#Summring multitype chunks 
def sumerise_chunks(chunks):
    """Process all chunks with AI Sumeries"""
    print("Processing Chunks with AI Sumeries")


    langchain_documents = []
    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        current_chunk = i +1
        print(f"Processing chunk {current_chunk} / {total_chunks}")

        #analyse chunk content

        content_data = separate_content_types(chunk)

        #Debug print

        print(f"Types found: {content_data['types']}")
        print(f"Tables: {len(content_data['tables'])}, Images :{len(content_data['images'])})")

        #create ai-enhanced sumary

        if content_data['tables'] or content_data['images']:
            print(f"Creating AI summary for mixed content...")
            try:
                enhanced_content = create_ai_enhanced_summary(
                    content_data['text'],
                    content_data['tables'],
                    content_data['images']
                )
                print(f" AI Summary Created successfulle")
                print(f"Enhanced Content preview: {enhanced_content[:200]}")
            except Exception as e:
                print(f"AI Sumary failed: {e}")
                enhanced_content=content_data['text']
        else:
            print(f"Using raw text (no table/images)")
            enhanced_content=content_data['text']
        #Create Langchain documents with metadata
        doc=Document(
            page_content=enhanced_content,
            metadata={
                "source": chunk.metadata.filename,             
                "page_number": chunk.metadata.page_number or 0, 
                "chunk_index": i,                               
                "types": ",".join(content_data["types"]),      
                "has_summary": bool(content_data["tables"] or content_data["images"]),
                "original_content":json.dumps({
                    "raw_text":content_data['text'],
                    "tables_html":content_data["tables"],
                    "images_base64":content_data['images']
                })
            }
        )

        langchain_documents.append(doc)

    print(f"Processed {len(langchain_documents)}")
    return langchain_documents

#Get the create vector store

def get_vectorstore():
    return PGVector(
        embeddings=OpenAIEmbeddings(model=EMBEDDING_MODEL),
        collection_name=COLLECTION_NAME,
        connection=DATABASE_URL,
        use_jsonb=True
    )


#Chains all the pipline and send the number of chunks

def ingest_file(file_path, user_id:int, document_id:int):
    elements = partition_document(file_path=file_path)
    chunks=create_chunk_by_title(elements=elements)
    docs=sumerise_chunks(chunks=chunks)
    for d in docs:
        d.metadata["user_id"] = user_id
        d.metadata["document_id"] = document_id
    get_vectorstore().add_documents(docs)
    return len(docs)
