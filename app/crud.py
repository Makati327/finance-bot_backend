from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas


def create_expense(db: Session, expense: schemas.ExpenseCreate):
    db_expense = models.Expense(
        amount=expense.amount,
        category=expense.category,
        note=expense.note,
        date=str(expense.date),
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expenses(db: Session):
    return db.query(models.Expense).order_by(models.Expense.date.desc()).all()