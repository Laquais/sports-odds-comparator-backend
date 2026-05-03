from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserBet
from ..schemas import UserBetCreate, UserBetResponse
from ..auth import get_current_user

router = APIRouter(prefix="/bets", tags=["Bets"])

@router.post("/", response_model=UserBetResponse, status_code=status.HTTP_201_CREATED)
def place_bet(
    bet_data: UserBetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserBet:
    """
    Enregistre un pari (Freebet ou autre) pour l'utilisateur connecté.
    """
    new_bet = UserBet(
        user_id=current_user.id,
        match_id=bet_data.match_id,
        bookmaker_name=bet_data.bookmaker_name,
        home_team=bet_data.home_team,
        away_team=bet_data.away_team,
        market_name=bet_data.market_name,
        outcome_label=bet_data.outcome_label,
        odds=bet_data.odds,
        stake=bet_data.stake,
        bet_type=bet_data.bet_type
    )

    db.add(new_bet)
    db.commit()
    db.refresh(new_bet)

    return new_bet