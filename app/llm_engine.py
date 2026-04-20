from google import genai
from app.config import settings
from app.rag_engine import retrieve_relevant_tips
from app.analyzer import get_spending_summary, generate_rule_based_insights

client = genai.Client(api_key=settings.GEMINI_API_KEY)


def build_context(df, user_query: str):
    summary = get_spending_summary(df)
    insights = generate_rule_based_insights(df)
    tips = []

    context = f"""
User spending summary:
- Total spent: ₹{summary['total_spent']:.2f}
- This week spent: ₹{summary['this_week_spent']:.2f}
- Top category: {summary['top_category']}
- Category totals: {summary['category_totals']}
- Daily spending: {summary['daily_spending']}

Rule-based insights:
{chr(10).join(['- ' + item for item in insights])}

Retrieved personal finance guidance:
{chr(10).join(['- ' + item for item in tips])}
"""
    return context, insights, tips


def ask_financial_assistant(df, user_query: str):
    context, insights, tips = build_context(df, user_query)

    prompt = f"""
You are a practical financial lifestyle assistant.

Your job:
- help the user spend more wisely in day-to-day life
- use their current spending data
- use retrieved finance guidance
- keep advice practical, realistic, and safe
- do not give investment advice
- do not shame the user

Answer in exactly these 3 sections:
1. Current situation
2. Recommendation
3. One practical action for today

User question:
{user_query}

Context:
{context}
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    answer = response.text if hasattr(response, "text") and response.text else "No response generated."

    return {
        "answer": answer,
        "retrieved_tips": tips,
        "insights": insights,
    }


def purchase_advisor(df, item_name: str, price: float):
    query = f"Should I buy {item_name} for ₹{price}?"
    context, insights, tips = build_context(df, query)

    prompt = f"""
You are a practical purchase advisor.

The user is considering buying:
- Item: {item_name}
- Price: ₹{price}

You must:
- evaluate the decision using the user's spending context
- use the retrieved finance guidance
- avoid extreme financial advice
- be balanced and practical

Answer in exactly these 3 sections:
1. Affordability view
2. Buy now, delay it, or skip it
3. One practical action

Context:
{context}
"""

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=prompt,
    )

    answer = response.text if hasattr(response, "text") and response.text else "No response generated."

    return {
        "answer": answer,
        "retrieved_tips": tips,
        "insights": insights,
    }