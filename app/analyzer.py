import pandas as pd


def expenses_to_dataframe(expenses):
    if not expenses:
        return pd.DataFrame(columns=["id", "amount", "category", "note", "date"])

    data = [
        {
            "id": e.id,
            "amount": e.amount,
            "category": e.category,
            "note": e.note,
            "date": e.date,
        }
        for e in expenses
    ]

    df = pd.DataFrame(data)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    return df


def get_spending_summary(df: pd.DataFrame):
    if df.empty:
        return {
            "total_spent": 0.0,
            "this_week_spent": 0.0,
            "top_category": "N/A",
            "category_totals": {},
            "daily_spending": {},
        }

    total_spent = float(df["amount"].sum())

    today = pd.Timestamp.today().normalize()
    week_ago = today - pd.Timedelta(days=7)
    this_week_df = df[df["date"] >= week_ago]
    this_week_spent = float(this_week_df["amount"].sum())

    category_totals_series = (
        df.groupby("category")["amount"].sum().sort_values(ascending=False)
    )
    category_totals = {
        k: float(v) for k, v in category_totals_series.to_dict().items()
    }

    top_category = (
        category_totals_series.index[0] if not category_totals_series.empty else "N/A"
    )

    daily_spending_series = (
        df.groupby(df["date"].dt.strftime("%Y-%m-%d"))["amount"]
        .sum()
        .sort_index()
    )
    daily_spending = {
        k: float(v) for k, v in daily_spending_series.to_dict().items()
    }

    return {
        "total_spent": total_spent,
        "this_week_spent": this_week_spent,
        "top_category": top_category,
        "category_totals": category_totals,
        "daily_spending": daily_spending,
    }


def generate_rule_based_insights(df: pd.DataFrame):
    if df.empty:
        return ["No expenses recorded yet. Add a few expenses to start getting useful advice."]

    insights = []

    today = pd.Timestamp.today().normalize()
    week_ago = today - pd.Timedelta(days=7)
    month_ago = today - pd.Timedelta(days=30)

    weekly_df = df[df["date"] >= week_ago]
    monthly_df = df[df["date"] >= month_ago]

    total_weekly = float(weekly_df["amount"].sum()) if not weekly_df.empty else 0.0

    food_spend = float(weekly_df[weekly_df["category"] == "Food"]["amount"].sum())
    shopping_spend = float(weekly_df[weekly_df["category"] == "Shopping"]["amount"].sum())
    entertainment_spend = float(
        weekly_df[weekly_df["category"] == "Entertainment"]["amount"].sum()
    )

    if food_spend > 1500:
        insights.append("Food spending is high this week. Cutting one or two takeout orders may help.")

    if shopping_spend > 2000:
        insights.append("Shopping spending is elevated this week. Review whether recent purchases were necessary.")

    if entertainment_spend > 1500:
        insights.append("Entertainment spending is above a normal casual range this week.")

    if total_weekly > 5000:
        insights.append("Your total spending this week looks high. Check non-essential categories first.")

    if not monthly_df.empty:
        unique_days = max(len(monthly_df["date"].dt.date.unique()), 1)
        avg_daily = float(monthly_df["amount"].sum()) / unique_days
        today_spend = float(df[df["date"].dt.date == today.date()]["amount"].sum())

        if today_spend > avg_daily * 1.8 and today_spend > 0:
            insights.append("Today's spending is much higher than your recent daily average.")

    if not insights:
        insights.append("Your spending pattern looks fairly stable right now.")

    return insights