from app.rag import generate_final_answer
from app.ingestion import get_vectorstore
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from app.config import JUDGE_MODEL
from dotenv import load_dotenv

load_dotenv()

db = get_vectorstore()
class Grade(BaseModel):
        explanation:str
        correct:bool

judge = ChatOpenAI(model=JUDGE_MODEL, temperature=0).with_structured_output(Grade)
from langsmith import Client
client = Client()

def target(inputs:dict)->dict:
    result = generate_final_answer(db,inputs["question"], chat_history=[])
    return {"answer":result["answer"]}


def correctness(inputs:dict, outputs:dict, reference_outputs:dict)->dict:
    prompt_text = f"""You are grading an answer to a question about a document.

QUESTION: {inputs["question"]}
REFERENCE ANSWER: {reference_outputs["answer"]}
STUDENT ANSWER: {outputs["answer"]}

Is the student answer factually consistent with the reference answer?
- Ignore differences in wording, and extra details that do not contradict the reference.
- If the reference says the information is not in the documents, the student answer is correct only if it also says it doesn't know."""

    grade = judge.invoke(prompt_text)

    return {"key": "correctness", "score": grade.correct, "comment": grade.explanation}



if __name__ == "__main__":
     client.evaluate(
    target,
    data="attention-paper-qa01",
    evaluators=[correctness],
    experiment_prefix="pgvector"
)