from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from math import ceil
from ..database import get_db
from ..models import User, Bookmaker, BookmakerType, UserBet
from ..schemas import FreebetListResponse, FreebetOpportunityResponse, BookmakerResponse, ExistingBetSummary
from ..auth import get_current_user

router = APIRouter(prefix="/freebets", tags=["Freebets"])


@router.get("/bookmakers", response_model=List[BookmakerResponse])
def get_all_bookmakers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    bookmakers = db.query(Bookmaker).filter(Bookmaker.type == BookmakerType.ARJEL).order_by(Bookmaker.name).all()
    return bookmakers


@router.get("/opportunities", response_model=FreebetListResponse)
def get_freebet_opportunities(
    bookmaker_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    where_clause = "WHERE bo.edge_freebet IS NOT NULL"
    params = {}

    if bookmaker_id:
        where_clause += " AND bo.bookmaker_id = :bookmaker_id"
        params["bookmaker_id"] = bookmaker_id

    count_query = text(f"""
            SELECT COUNT(*) as total
            FROM bookmaker_odd AS bo
            JOIN outcome AS o ON o.id = bo.outcome_id
            JOIN match_market AS mm ON mm.id = o.match_market_id
            JOIN `match` AS m ON m.id = mm.match_id
            JOIN market AS mk ON mk.id = mm.market_id
            JOIN team AS ht ON ht.id = m.home_team_id
            JOIN team AS at ON at.id = m.away_team_id
            JOIN bookmaker AS b ON b.id = bo.bookmaker_id
            {where_clause}
        """)

    count_result = db.execute(count_query, params)
    total = count_result.scalar()

    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    data_query = text(f"""
        SELECT
            bo.edge_freebet,
            bo.odds,
            m.id as match_id,
            m.start_time,
            ht.name AS home_team_name,
            at.name AS away_team_name,
            mk.name AS market_name,
            o.label AS outcome_label,
            b.name AS bookmaker_name
        FROM bookmaker_odd AS bo
        JOIN outcome AS o ON o.id = bo.outcome_id
        JOIN match_market AS mm ON mm.id = o.match_market_id
        JOIN `match` AS m ON m.id = mm.match_id
        JOIN market AS mk ON mk.id = mm.market_id
        JOIN team AS ht ON ht.id = m.home_team_id
        JOIN team AS at ON at.id = m.away_team_id
        JOIN bookmaker AS b ON b.id = bo.bookmaker_id
        {where_clause}
        ORDER BY bo.edge_freebet DESC
        LIMIT :limit OFFSET :offset
    """)

    result = db.execute(data_query, params)
    rows = result.fetchall()

    items = []
    match_ids = [row[2] for row in rows] if rows else []
    user_bets = []
    if match_ids:
        user_bets = db.query(UserBet).filter(
            UserBet.user_id == current_user.id,
            UserBet.match_id.in_(match_ids)
        ).all()

    for row in rows:
        match_id = row[2]
        market_name = row[6]
        outcome_label = row[7]

        matching_bets = [
            ExistingBetSummary(
                bookmaker_name=bet.bookmaker_name,
                stake=bet.stake,
                bet_type=bet.bet_type
            )
            for bet in user_bets
            if bet.match_id == match_id
               and bet.market_name == market_name
               and bet.outcome_label == outcome_label
        ]

        items.append(FreebetOpportunityResponse(
            edge_freebet=row[0],
            odds=row[1],
            match_id=match_id,
            start_time=row[3],
            home_team_name=row[4],
            away_team_name=row[5],
            market_name=market_name,
            outcome_label=outcome_label,
            bookmaker_name=row[8],
            existing_bets=matching_bets
        ))

    total_pages = ceil(total / page_size) if total > 0 else 1

    return FreebetListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
