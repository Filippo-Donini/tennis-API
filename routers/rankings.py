from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Annotated
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sys
sys.path.insert(0, "./../")
from database import get_db
from models import AtpRankingsCurrent, WtaRankingsCurrent
from sqlalchemy import Integer

router = APIRouter()
templates = Jinja2Templates(directory="templates")

db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/", response_class=HTMLResponse)
async def rankings_page(
    request: Request,
    db: db_dependency,
    tour: str = Query("ATP", regex="^(ATP|WTA)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=100)
):
    """Display current rankings for ATP or WTA tours"""
    try:
        # Determine which model to use based on tour
        RankingsModel = AtpRankingsCurrent if tour == "ATP" else WtaRankingsCurrent
        
        # Get the latest ranking date
        latest_date = db.query(func.max(RankingsModel.ranking_date)).scalar()

        if latest_date:
            # Calculate offset for pagination
            offset = (page - 1) * per_page
            
            # Get rankings with pagination
            rankings = db.query(RankingsModel)\
                .filter(RankingsModel.ranking_date == latest_date)\
                .order_by(RankingsModel.rank.cast(Integer))\
                .offset(offset)\
                .limit(per_page)\
                .all()
            
            # Get total count
            total_count = db.query(RankingsModel)\
                .filter(RankingsModel.ranking_date == latest_date)\
                .count()
            
            total_pages = (total_count + per_page - 1) // per_page
            
            return templates.TemplateResponse(
                "rankings.html",
                {
                    "request": request,
                    "rankings": rankings,
                    "tour": tour,
                    "current_page": page,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1,
                    "latest_date": latest_date,
                    "total_count": total_count,
                    "showing_start": offset + 1,
                    "showing_end": min(offset + per_page, total_count)
                }
            )
        else:
            return templates.TemplateResponse(
                "rankings.html",
                {
                    "request": request,
                    "rankings": [],
                    "tour": tour,
                    "error": "No rankings data available"
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add API endpoint for getting rankings data
@router.get("/api")
async def get_rankings(
    db: db_dependency,
    tour: str = Query("ATP", regex="^(ATP|WTA)$"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=10, le=100)
):
    """Get rankings data in JSON format"""
    try:
        RankingsModel = AtpRankingsCurrent if tour == "ATP" else WtaRankingsCurrent
        latest_date = db.query(func.max(RankingsModel.ranking_date)).scalar()

        if latest_date:
            offset = (page - 1) * per_page
            rankings = db.query(RankingsModel)\
                .filter(RankingsModel.ranking_date == latest_date)\
                .order_by(RankingsModel.rank.cast(Integer))\
                .offset(offset)\
                .limit(per_page)\
                .all()

            total_count = db.query(RankingsModel)\
                .filter(RankingsModel.ranking_date == latest_date)\
                .count()

            return {
                "rankings": [
                    {
                        "rank": r.rank,
                        "name": r.name,
                        "age": r.age,
                        "country": r.country,
                        "points": r.points,
                        "ranking_date": r.ranking_date.isoformat()
                    }
                    for r in rankings
                ],
                "total_count": total_count,
                "page": page,
                "per_page": per_page,
                "total_pages": (total_count + per_page - 1) // per_page,
                "latest_date": latest_date.isoformat()
            }
        else:
            return {
                "rankings": [],
                "error": "No rankings data available"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))