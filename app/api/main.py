from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.evaluation.evaluator import evaluate_dataset
from app.guardrails.response_guard import check_response

app = FastAPI(
    title="LLM Evaluation & Guardrails API",
    description="Evaluate LLM responses and check basic safety issues.",
    version="1.0.0",
)


class EvaluationRequest(BaseModel):
    cases: list[dict]


class GuardrailRequest(BaseModel):
    answer: str
    context: str


@app.get("/")
def health_check():
    return {"status": "healthy"}


@app.post("/evaluate")
def evaluate(request: EvaluationRequest):
    try:
        return evaluate_dataset(request.cases)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/guardrails/check")
def guardrails_check(request: GuardrailRequest):
    return check_response(request.answer, request.context)