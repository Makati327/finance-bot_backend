from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app import schemas, crud
from app.analyzer import (
    expenses_to_dataframe,
    get_spending_summary,
    generate_rule_based_insights,
)
from app.rag_engine import load_knowledge_base
from app.llm_engine import ask_financial_assistant, purchase_advisor
from app.utils import health_message

Base.metadata.create_all(bind=engine)
load_knowledge_base()

app = FastAPI(title="AI Financial Lifestyle Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return health_message()


@app.post("/expenses", response_model=schemas.ExpenseResponse)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return crud.create_expense(db, expense)


@app.get("/expenses", response_model=list[schemas.ExpenseResponse])
def list_expenses(db: Session = Depends(get_db)):
    return crud.get_expenses(db)


@app.get("/dashboard", response_model=schemas.DashboardResponse)
def dashboard(db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db)
    df = expenses_to_dataframe(expenses)

    summary = get_spending_summary(df)
    insights = generate_rule_based_insights(df)

    return {
        "total_spent": summary["total_spent"],
        "this_week_spent": summary["this_week_spent"],
        "top_category": summary["top_category"],
        "category_totals": summary["category_totals"],
        "daily_spending": summary["daily_spending"],
        "insights": insights,
    }


@app.post("/ask", response_model=schemas.AskResponse)
def ask_assistant(payload: schemas.AskRequest, db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db)
    df = expenses_to_dataframe(expenses)
    return ask_financial_assistant(df, payload.question)


@app.post("/purchase-advisor", response_model=schemas.PurchaseAdvisorResponse)
def purchase_advice(payload: schemas.PurchaseAdvisorRequest, db: Session = Depends(get_db)):
    expenses = crud.get_expenses(db)
    df = expenses_to_dataframe(expenses)
    return purchase_advisor(df, payload.item_name, payload.price)