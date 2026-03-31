"""
Activity log routes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models import User, ActivityLog
from app.schemas import ActivityLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/activity", tags=["Activity Log"])


@router.get("", response_model=List[ActivityLogResponse])
def get_activity_log(
    limit: int = Query(50, ge=1, le=200),
    action_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get activity log entries, newest first."""
    query = db.query(ActivityLog).order_by(ActivityLog.timestamp.desc())

    if action_type:
        query = query.filter(ActivityLog.action_type == action_type)

    logs = query.limit(limit).all()

    results = []
    for log in logs:
        user = db.query(User).filter(User.id == log.user_id).first()
        results.append(ActivityLogResponse(
            id=log.id,
            action_type=log.action_type,
            action_description=log.action_description,
            item_name=log.item_name,
            item_id=log.item_id,
            detail=log.detail,
            user_id=log.user_id,
            user_name=user.full_name if user else "Unknown",
            timestamp=log.timestamp,
        ))

    return results
