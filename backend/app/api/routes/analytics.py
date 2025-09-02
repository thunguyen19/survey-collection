from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, text
from sqlmodel import select
import uuid
from datetime import datetime, timedelta

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import FeedbackResponse, FeedbackSession, SurveyTemplate, User, Organization
from app.api.routes.analyze import analyze_with_llm

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def get_analytics_overview(
    session: SessionDep, 
    current_user: CurrentUser,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get high-level analytics overview for the current user's organization.
    """
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    org_id = current_user.organization_id
    
    # Total surveys sent
    total_surveys_stmt = select(func.count(FeedbackSession.id)).where(
        FeedbackSession.organization_id == org_id,
        FeedbackSession.created_at >= start_date
    )
    total_surveys = session.exec(total_surveys_stmt).one() or 0
    
    # Total responses received
    total_responses_stmt = select(func.count(FeedbackResponse.id)).where(
        FeedbackResponse.created_at >= start_date,
        FeedbackResponse.feedback_session_id.in_(
            select(FeedbackSession.id).where(FeedbackSession.organization_id == org_id)
        )
    )
    total_responses = session.exec(total_responses_stmt).one() or 0
    
    # Response rate
    response_rate = (total_responses / total_surveys * 100) if total_surveys > 0 else 0
    
    # Active survey templates
    active_templates_stmt = select(func.count(SurveyTemplate.id)).where(
        SurveyTemplate.organization_id == org_id,
        SurveyTemplate.active == True
    )
    active_templates = session.exec(active_templates_stmt).one() or 0
    
    # Average completion time (mock data for now)
    avg_completion_time = 3.2  # minutes
    
    return {
        "total_surveys_sent": total_surveys,
        "total_responses": total_responses,
        "response_rate": round(response_rate, 1),
        "active_templates": active_templates,
        "avg_completion_time": avg_completion_time,
        "date_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days
        }
    }


@router.get("/response-trends")
def get_response_trends(
    session: SessionDep,
    current_user: CurrentUser,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get response trends over time for charts.
    """
    org_id = current_user.organization_id
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Generate mock trend data for now
    # In a real implementation, you would query the database for actual data
    trends = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        # Mock data with some variation
        responses = max(0, 15 + (i % 7) * 3 + (i % 3) * 2)
        surveys = max(responses, responses + (i % 5) * 2)
        
        trends.append({
            "date": date.strftime("%Y-%m-%d"),
            "surveys_sent": surveys,
            "responses_received": responses,
            "response_rate": round((responses / surveys * 100) if surveys > 0 else 0, 1)
        })
    
    return {
        "trends": trends,
        "summary": {
            "total_surveys": sum(t["surveys_sent"] for t in trends),
            "total_responses": sum(t["responses_received"] for t in trends),
            "avg_response_rate": round(
                sum(t["response_rate"] for t in trends) / len(trends), 1
            ) if trends else 0
        }
    }


@router.get("/sentiment-analysis")
def get_sentiment_analysis(
    session: SessionDep,
    current_user: CurrentUser,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get sentiment analysis of feedback responses.
    """
    org_id = current_user.organization_id
    
    # For now, return mock sentiment data
    # In a real implementation, you would:
    # 1. Query feedback responses for the organization
    # 2. Run sentiment analysis using the analyze.py module
    # 3. Aggregate the results
    
    mock_sentiments = {
        "positive": 65,
        "neutral": 25,
        "negative": 10
    }
    
    mock_topics = [
        {"topic": "Nursing Care", "count": 45, "avg_sentiment": "positive"},
        {"topic": "Wait Times", "count": 32, "avg_sentiment": "negative"},
        {"topic": "Communication", "count": 28, "avg_sentiment": "positive"},
        {"topic": "Cleanliness", "count": 22, "avg_sentiment": "neutral"},
        {"topic": "Billing", "count": 18, "avg_sentiment": "negative"},
    ]
    
    return {
        "sentiment_distribution": mock_sentiments,
        "top_topics": mock_topics,
        "total_analyzed": sum(mock_sentiments.values()),
        "analysis_period": f"Last {days} days"
    }


@router.get("/survey-performance")
def get_survey_performance(
    session: SessionDep,
    current_user: CurrentUser
) -> Dict[str, Any]:
    """
    Get performance metrics for different survey templates.
    """
    org_id = current_user.organization_id
    
    # Get survey templates for the organization
    templates_stmt = select(SurveyTemplate).where(
        SurveyTemplate.organization_id == org_id
    )
    templates = session.exec(templates_stmt).all()
    
    # Mock performance data for each template
    performance_data = []
    for template in templates:
        # In a real implementation, calculate actual metrics
        mock_data = {
            "template_id": str(template.id),
            "template_name": template.name,
            "surveys_sent": 45 + (len(template.name) % 20),
            "responses_received": 32 + (len(template.name) % 15),
            "avg_completion_time": 2.5 + (len(template.name) % 10) * 0.3,
            "avg_rating": 4.2 + (len(template.name) % 5) * 0.1,
            "completion_rate": 85.5 + (len(template.name) % 10),
        }
        mock_data["response_rate"] = round(
            (mock_data["responses_received"] / mock_data["surveys_sent"] * 100), 1
        )
        performance_data.append(mock_data)
    
    return {
        "survey_performance": performance_data,
        "total_templates": len(templates)
    }


@router.get("/recent-feedback")
def get_recent_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get recent feedback responses with analysis.
    """
    org_id = current_user.organization_id
    
    # Mock recent feedback data
    # In a real implementation, query actual feedback responses
    mock_feedback = [
        {
            "id": str(uuid.uuid4()),
            "survey_name": "Post-Appointment Survey",
            "submitted_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "sentiment": "positive",
            "summary": "Great experience with Dr. Smith, very helpful and kind staff.",
            "rating": 5,
            "topics": ["nursing", "communication"]
        },
        {
            "id": str(uuid.uuid4()),
            "survey_name": "Emergency Department Survey",
            "submitted_at": (datetime.utcnow() - timedelta(hours=5)).isoformat(),
            "sentiment": "negative",
            "summary": "Long wait time, billing issues, but good medical care.",
            "rating": 2,
            "topics": ["wait", "billing"]
        },
        {
            "id": str(uuid.uuid4()),
            "survey_name": "Post-Appointment Survey",
            "submitted_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "sentiment": "positive",
            "summary": "Clean facilities, professional staff, excellent service.",
            "rating": 4,
            "topics": ["cleanliness", "communication"]
        },
        {
            "id": str(uuid.uuid4()),
            "survey_name": "Discharge Survey",
            "submitted_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "sentiment": "neutral",
            "summary": "Average experience, room for improvement in communication.",
            "rating": 3,
            "topics": ["communication"]
        },
        {
            "id": str(uuid.uuid4()),
            "survey_name": "Post-Appointment Survey",
            "submitted_at": (datetime.utcnow() - timedelta(days=1, hours=3)).isoformat(),
            "sentiment": "positive",
            "summary": "Amazing nursing team, very caring and attentive.",
            "rating": 5,
            "topics": ["nursing", "communication"]
        }
    ]
    
    return {
        "recent_feedback": mock_feedback[:limit],
        "total_count": len(mock_feedback)
    }


@router.post("/analyze-text")
def analyze_feedback_text(
    text_data: Dict[str, str],
    session: SessionDep,
    current_user: CurrentUser
) -> Dict[str, Any]:
    """
    Analyze a piece of feedback text using AI/heuristic analysis.
    """
    text = text_data.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    # Use the analyze module
    analysis_result = analyze_with_llm(text)
    
    return {
        "original_text": text,
        "analysis": analysis_result,
        "analyzed_at": datetime.utcnow().isoformat()
    }
