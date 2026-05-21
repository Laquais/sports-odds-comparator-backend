from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    password_confirm: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class SportResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class LeagueResponse(BaseModel):
    id: int
    name: str
    sport_id: int

    class Config:
        from_attributes = True


class TeamResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class MatchResponse(BaseModel):
    id: int
    sport_id: int
    league_id: Optional[int]
    home_team_id: Optional[int] = None
    away_team_id: Optional[int] = None
    start_time: datetime
    home_team: Optional[TeamResponse] = None
    away_team: Optional[TeamResponse] = None
    league: Optional[LeagueResponse] = None

    class Config:
        from_attributes = True


class BookmakerResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class BookmakerOddResponse(BaseModel):
    bookmaker: BookmakerResponse
    odds: Optional[float]
    edge_odds: Optional[float]
    last_update: datetime

    class Config:
        from_attributes = True


class OutcomeResponse(BaseModel):
    id: int
    label: str
    fair_odds: Optional[float]
    bookmaker_odds: List[BookmakerOddResponse]
    best_odd: Optional[float] = None
    best_bookmaker: Optional[str] = None

    class Config:
        from_attributes = True


class MarketResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class MatchMarketResponse(BaseModel):
    id: int
    market: MarketResponse
    line: Optional[float]
    period: Optional[str]
    outcomes: List[OutcomeResponse]

    class Config:
        from_attributes = True


class MatchOddsResponse(BaseModel):
    match: MatchResponse
    markets: List[MatchMarketResponse]

    class Config:
        from_attributes = True


class BestOutcomeOddsResponse(BaseModel):
    value: float
    bookmakers: List[str]


class MatchWithBestOddsResponse(MatchResponse):
    best_odds: dict[str, Optional[BestOutcomeOddsResponse]]


class ExistingBetSummary(BaseModel):
    bookmaker_name: str
    stake: float
    bet_type: str

    class Config:
        from_attributes = True


class FreebetOpportunityResponse(BaseModel):
    edge_freebet: float
    odds: float
    start_time: datetime
    home_team_name: str
    away_team_name: str
    market_name: str
    outcome_label: str
    match_id: int
    bookmaker_name: str
    existing_bets: List[ExistingBetSummary] = []

    class Config:
        from_attributes = True


class FreebetListResponse(BaseModel):
    items: List[FreebetOpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BestEVOpportunityResponse(BaseModel):
    edge_odds: float
    odds: float
    sport_name: str
    home_team_name: str
    away_team_name: str
    market_name: str
    market_line: Optional[float]
    outcome_label: str
    start_time: datetime
    match_id: int
    bookmaker_name: str

    class Config:
        from_attributes = True


class BestEVListResponse(BaseModel):
    items: List[BestEVOpportunityResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserBetCreate(BaseModel):
    match_id: int
    bookmaker_name: str
    home_team: str
    away_team: str
    market_name: str
    outcome_label: str
    odds: float
    stake: float
    bet_type: str = "freebet"


class UserBetResponse(UserBetCreate):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
