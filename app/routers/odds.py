from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, exists, distinct
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user
from ..database import get_db
from ..models import User, Sport, League, Match, MatchMarket, Outcome, BookmakerOdd, Bookmaker, Market, Team
from ..schemas import (
    SportResponse,
    LeagueResponse,
    MatchResponse,
    MatchOddsResponse,
    MatchMarketResponse,
    OutcomeResponse,
    BookmakerOddResponse,
    BookmakerResponse,
    MarketResponse,
    MarketOptionsResponse,
    MatchWithBestOddsResponse,
    BestOutcomeOddsResponse,
    BestEVOpportunityResponse,
    BestEVListResponse
)

router = APIRouter(tags=["Odds"])


@router.get("/bookmakers", response_model=List[BookmakerResponse])
def get_bookmakers(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    bookmakers = db.query(Bookmaker).order_by(Bookmaker.name).all()
    return bookmakers


@router.get("/sports", response_model=List[SportResponse])
def get_sports(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    sports = db.query(Sport).filter(
        exists().where(Match.sport_id == Sport.id)
    ).order_by(Sport.name).all()
    return sports


@router.get("/sports/{sport_id}/leagues", response_model=List[LeagueResponse])
def get_leagues_by_sport(
        sport_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")

    leagues = db.query(League).filter(League.sport_id == sport_id).order_by(League.name).all()
    return leagues


@router.get("/sports/{sport_id}/matches", response_model=List[MatchResponse])
def get_matches_by_sport(
        sport_id: int,
        league_ids: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        search: Optional[str] = Query(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")

    query = db.query(Match).filter(Match.sport_id == sport_id, Match.is_live == False)

    if league_ids:
        league_id_list = [int(x) for x in league_ids.split(',')]
        query = query.filter(Match.league_id.in_(league_id_list))

    if start_date:
        query = query.filter(Match.start_time >= start_date)
    if end_date:
        query = query.filter(Match.start_time <= end_date)

    if search:
        search_pattern = f"%{search}%"
        query = query.join(Match.home_team.of_type(Team)).filter(
            or_(
                Team.name.like(search_pattern),
                Match.away_team.has(Team.name.like(search_pattern))
            )
        )

    matches = query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.league)
    ).order_by(Match.start_time).all()

    return matches


@router.get("/leagues/{league_id}/matches", response_model=List[MatchResponse])
def get_matches_by_league(
        league_id: int,
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    query = db.query(Match).filter(Match.league_id == league_id)

    if start_date:
        query = query.filter(Match.start_time >= start_date)
    if end_date:
        query = query.filter(Match.start_time <= end_date)

    matches = query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.league)
    ).order_by(Match.start_time).all()

    return matches


@router.get("/matches/{match_id}/odds", response_model=MatchOddsResponse)
def get_match_odds(
        match_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    match = db.query(Match).options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.league)
    ).filter(Match.id == match_id).first()

    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    match_markets = db.query(MatchMarket).options(
        joinedload(MatchMarket.market),
        joinedload(MatchMarket.outcomes).joinedload(Outcome.bookmaker_odds).joinedload(BookmakerOdd.bookmaker)
    ).filter(MatchMarket.match_id == match_id).all()

    markets_response = []
    for mm in match_markets:
        outcomes_response = []
        for outcome in mm.outcomes:
            bookmaker_odds_response = []
            best_odd = None
            best_bookmaker = None

            for bo in outcome.bookmaker_odds:
                bookmaker_odds_response.append(BookmakerOddResponse(
                    bookmaker=BookmakerResponse(
                        id=bo.bookmaker.id,
                        name=bo.bookmaker.name
                    ),
                    odds=bo.odds,
                    edge_odds=bo.edge_odds,
                    last_update=bo.last_update
                ))

                if bo.odds is not None and (best_odd is None or bo.odds > best_odd):
                    best_odd = bo.odds
                    best_bookmaker = bo.bookmaker.name

            outcomes_response.append(OutcomeResponse(
                id=outcome.id,
                label=outcome.label,
                fair_odds=outcome.fair_odds,
                bookmaker_odds=bookmaker_odds_response,
                best_odd=best_odd,
                best_bookmaker=best_bookmaker
            ))

        markets_response.append(MatchMarketResponse(
            id=mm.id,
            market=mm.market,
            line=mm.line,
            period=mm.period,
            outcomes=outcomes_response
        ))

    return MatchOddsResponse(
        match=match,
        markets=markets_response
    )


@router.get("/sports/{sport_id}/markets", response_model=List[MarketResponse])
def get_markets_by_sport(
        sport_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")

    markets = (
        db.query(Market)
        .filter(Market.sport_id == sport_id)
        .order_by(Market.name)
        .all()
    )
    return markets


@router.get("/sports/{sport_id}/markets/{market_id}/options", response_model=MarketOptionsResponse)
def get_market_options(
        sport_id: int,
        market_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    base = (
        db.query(MatchMarket)
        .join(Match, MatchMarket.match_id == Match.id)
        .filter(Match.sport_id == sport_id, MatchMarket.market_id == market_id)
    )

    period_rows = base.with_entities(distinct(MatchMarket.period)).filter(MatchMarket.period.isnot(None)).all()
    line_rows = base.with_entities(distinct(MatchMarket.line)).filter(MatchMarket.line.isnot(None)).all()

    periods = sorted(r[0].value for r in period_rows)
    lines = sorted(r[0] for r in line_rows)

    return MarketOptionsResponse(periods=periods, lines=lines)


@router.get(
    "/sports/{sport_id}/matches-with-odds",
    response_model=List[MatchWithBestOddsResponse],
)
def get_matches_with_best_odds(
        sport_id: int,
        league_ids: Optional[str] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        search: Optional[str] = Query(None),
        market_id: int = Query(..., description="ID du marché (market.id)"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
):
    sport = db.query(Sport).filter(Sport.id == sport_id).first()
    if not sport:
        raise HTTPException(status_code=404, detail="Sport not found")

    # Si market_id n'est pas fourni → récupérer l'id du marché "ml" pour ce sport
    if market_id is None:
        ml_market = (
            db.query(Market)
            .filter(Market.sport_id == sport_id, Market.name == "ml")
            .first()
        )
        if not ml_market:
            raise HTTPException(status_code=400, detail="Default market 'ml' not found for this sport")
        market_id = ml_market.id

    query = db.query(Match).filter(Match.sport_id == sport_id)

    if league_ids:
        league_id_list = [int(x) for x in league_ids.split(",")]
        query = query.filter(Match.league_id.in_(league_id_list))

    if start_date:
        query = query.filter(Match.start_time >= start_date)
    if end_date:
        query = query.filter(Match.start_time <= end_date)

    if search:
        search_pattern = f"%{search}%"
        query = query.join(Match.home_team.of_type(Team)).filter(
            or_(
                Team.name.like(search_pattern),
                Match.away_team.has(Team.name.like(search_pattern)),
            )
        )

    matches = query.options(
        joinedload(Match.home_team),
        joinedload(Match.away_team),
        joinedload(Match.league),

        # branche 1 : marché
        joinedload(Match.match_markets).joinedload(MatchMarket.market),

        # branche 2 : outcomes + bookmaker_odds + bookmaker
        joinedload(Match.match_markets)
        .joinedload(MatchMarket.outcomes)
        .joinedload(Outcome.bookmaker_odds)
        .joinedload(BookmakerOdd.bookmaker),
    ).order_by(Match.start_time).all()

    result: List[MatchWithBestOddsResponse] = []

    for m in matches:
        # on récupère le MatchMarket correspondant au marché demandé
        mm_for_market = next(
            (mm for mm in m.match_markets if mm.market_id == market_id),
            None,
        )

        best_odds_map: dict[str, Optional[BestOutcomeOddsResponse]] = {
            "home": None,
            "draw": None,
            "away": None,
        }

        if mm_for_market:
            for outcome in mm_for_market.outcomes:
                label_norm = outcome.label.lower()

                if "domicile" in label_norm or "home" in label_norm or "1" == label_norm:
                    key = "home"
                elif "nul" in label_norm or "draw" in label_norm or "x" == label_norm:
                    key = "draw"
                else:
                    key = "away"

                if not outcome.bookmaker_odds:
                    continue

                values = [bo.odds for bo in outcome.bookmaker_odds if bo.odds is not None]
                if not values:
                    continue

                best_value = max(values)
                EPS = 1e-6
                best_books = [
                    bo.bookmaker.name
                    for bo in outcome.bookmaker_odds
                    if bo.odds is not None and abs(bo.odds - best_value) < EPS
                ]

                best_odds_map[key] = BestOutcomeOddsResponse(
                    value=best_value,
                    bookmakers=best_books,
                )

            result.append(
                MatchWithBestOddsResponse(
                    **MatchResponse.from_orm(m).dict(),
                    best_odds=best_odds_map,
                )
            )

    return result


@router.get("/best-ev", response_model=BestEVListResponse)
def get_best_ev_opportunities(
        bookmaker_id: Optional[int] = Query(None),
        min_odds: Optional[float] = Query(None),
        max_odds: Optional[float] = Query(None),
        min_ev: Optional[float] = Query(None),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    query = (
        db.query(
            BookmakerOdd.edge_odds,
            BookmakerOdd.odds,
            Sport.name.label('sport_name'),
            Market.name.label('market_name'),
            MatchMarket.line.label('market_line'),
            Outcome.label.label('outcome_label'),
            Match.start_time,
            Match.id.label('match_id'),
            Bookmaker.name.label('bookmaker_name')
        )
        .join(Outcome, BookmakerOdd.outcome_id == Outcome.id)
        .join(MatchMarket, Outcome.match_market_id == MatchMarket.id)
        .join(Match, MatchMarket.match_id == Match.id)
        .join(Sport, Match.sport_id == Sport.id)
        .join(Market, MatchMarket.market_id == Market.id)
        .join(Bookmaker, BookmakerOdd.bookmaker_id == Bookmaker.id)
        .filter(BookmakerOdd.edge_odds.isnot(None), Match.is_live == False)
    )

    if bookmaker_id:
        query = query.filter(BookmakerOdd.bookmaker_id == bookmaker_id)

    if min_odds is not None:
        query = query.filter(BookmakerOdd.odds >= min_odds)

    if max_odds is not None:
        query = query.filter(BookmakerOdd.odds <= max_odds)

    if min_ev is not None:
        query = query.filter(BookmakerOdd.edge_odds >= min_ev)

    if start_date:
        query = query.filter(Match.start_time >= start_date)

    if end_date:
        query = query.filter(Match.start_time <= end_date)

    query = query.order_by(BookmakerOdd.edge_odds.desc())

    total = query.count()

    offset = (page - 1) * page_size
    results = query.offset(offset).limit(page_size).all()

    items = []
    for row in results:
        match = db.query(Match).options(
            joinedload(Match.home_team),
            joinedload(Match.away_team)
        ).filter(Match.id == row.match_id).first()

        items.append(BestEVOpportunityResponse(
            edge_odds=row.edge_odds,
            odds=row.odds,
            sport_name=row.sport_name,
            home_team_name=match.home_team.name,
            away_team_name=match.away_team.name,
            market_name=row.market_name,
            market_line=row.market_line,
            outcome_label=row.outcome_label,
            start_time=row.start_time,
            match_id=row.match_id,
            bookmaker_name=row.bookmaker_name
        ))

    total_pages = (total + page_size - 1) // page_size

    return BestEVListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
