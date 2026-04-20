from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import date


class ExpenseCreate(BaseModel):
    amount: float
    category: str
    note: Optional[str] = None
    date: date


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    note: Optional[str]
    date: str

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    total_spent: float
    this_week_spent: float
    top_category: str
    category_totals: Dict[str, float]
    daily_spending: Dict[str, float]
    insights: List[str]


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    retrieved_tips: List[str]
    insights: List[str]


class PurchaseAdvisorRequest(BaseModel):
    item_name: str
    price: float


class PurchaseAdvisorResponse(BaseModel):
    answer: str
    retrieved_tips: List[str]
    insights: List[str]