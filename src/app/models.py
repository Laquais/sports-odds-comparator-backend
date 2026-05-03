import enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, UniqueConstraint, Index, Text, Enum
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class BookmakerType(enum.Enum):
    HA = "HA"
    ARJEL = "ARJEL"


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class UserBet(Base):
    __tablename__ = 'user_bet'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    match_id = Column(Integer, nullable=False)
    bookmaker_name = Column(String(50), nullable=False)
    sport_name = Column(String(50), nullable=True)
    home_team = Column(String(70), nullable=True)
    away_team = Column(String(70), nullable=True)
    market_name = Column(String(50), nullable=True)
    outcome_label = Column(String(50), nullable=True)
    odds = Column(Float, nullable=False)
    stake = Column(Float, nullable=False)
    bet_type = Column(String(20), default="freebet")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class Bookmaker(Base):
    __tablename__ = 'bookmaker'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True, index=True)
    type = Column(Enum(BookmakerType, name="bookmaker_type"), nullable=False)

    sports = relationship("BookmakerSport", back_populates="bookmaker", cascade="all, delete-orphan")
    leagues = relationship("BookmakerLeague", back_populates="bookmaker", cascade="all, delete-orphan")
    matches = relationship("BookmakerMatch", back_populates="bookmaker", cascade="all, delete-orphan")
    teams = relationship("BookmakerTeam", back_populates="bookmaker", cascade="all, delete-orphan")


class Sport(Base):
    __tablename__ = 'sport'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False, unique=True, index=True)

    bookmaker_sports = relationship("BookmakerSport", back_populates="sport", cascade="all, delete-orphan")
    leagues = relationship("League", back_populates="sport", cascade="all, delete-orphan")
    markets = relationship("Market", back_populates="sport", cascade="all, delete-orphan")
    teams = relationship("Team", back_populates="sport", cascade="all, delete-orphan")


class BookmakerSport(Base):
    __tablename__ = 'bookmaker_sport'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmaker.id', ondelete="CASCADE"))
    sport_id = Column(Integer, ForeignKey('sport.id', ondelete="CASCADE"))
    bookmaker_sport_id = Column(String(40), nullable=False)
    bookmaker_sport_name = Column(String(50), nullable=False)

    bookmaker = relationship("Bookmaker", back_populates="sports")
    sport = relationship("Sport", back_populates="bookmaker_sports")

    __table_args__ = (
        UniqueConstraint('bookmaker_id', 'sport_id', name='uix_bookmaker_sport'),
        Index('ix_bookmaker_sport_bookmaker_id_sport_id', 'bookmaker_id', 'sport_id'),
        Index('ix_bookmaker_sport_bookmaker_id_bookmaker_sport_id', 'bookmaker_id', 'bookmaker_sport_id'),
    )


class League(Base):
    __tablename__ = 'league'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, ForeignKey('sport.id'))
    name = Column(String(100), nullable=False)

    sport = relationship("Sport", back_populates="leagues")
    bookmaker_leagues = relationship("BookmakerLeague", back_populates="league")
    matches = relationship("Match", back_populates="league")

    __table_args__ = (
        UniqueConstraint('sport_id', 'name', name='uix_sport_league_name'),
        Index('ix_league_sport_id_name', 'sport_id', 'name'),
    )


class BookmakerLeague(Base):
    __tablename__ = 'bookmaker_league'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmaker.id', ondelete="CASCADE"))
    league_id = Column(Integer, ForeignKey('league.id', ondelete="CASCADE"))
    bookmaker_league_id = Column(String(40), nullable=False)
    bookmaker_league_name = Column(String(70), nullable=False)

    bookmaker = relationship("Bookmaker", back_populates="leagues")
    league = relationship("League", back_populates="bookmaker_leagues")

    __table_args__ = (
        UniqueConstraint('bookmaker_id', 'league_id', name='uix_bookmaker_league'),
        Index('ix_bookmaker_league_bookmaker_id_league_id', 'bookmaker_id', 'league_id'),
        Index('ix_bookmaker_league_bookmaker_id_bookmaker_league_id', 'bookmaker_id', 'bookmaker_league_id'),
    )


class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, ForeignKey('sport.id', ondelete="CASCADE"), nullable=False)
    league_id = Column(Integer, ForeignKey('league.id', ondelete="CASCADE"))
    home_team_id = Column(Integer, ForeignKey('team.id', ondelete="CASCADE"), nullable=False)
    away_team_id = Column(Integer, ForeignKey('team.id', ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)

    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    bookmaker_matches = relationship("BookmakerMatch", back_populates="match", cascade="all, delete-orphan")
    match_markets = relationship("MatchMarket", back_populates="match", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_match_league_id', 'league_id'),
        Index('ix_match_all', 'sport_id', 'league_id', 'home_team_id', 'away_team_id'),
    )


class BookmakerMatch(Base):
    __tablename__ = 'bookmaker_match'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmaker.id', ondelete="CASCADE"))
    match_id = Column(Integer, ForeignKey('match.id', ondelete="CASCADE"))
    bookmaker_match_id = Column(String(40), nullable=False)

    bookmaker = relationship("Bookmaker", back_populates="matches")
    match = relationship("Match", back_populates="bookmaker_matches")

    __table_args__ = (
        UniqueConstraint('bookmaker_id', 'match_id', name='uix_bookmaker_match'),
        Index('ix_bookmaker_match_bookmaker_id_match_id', 'bookmaker_id', 'match_id'),
        Index('ix_bookmaker_match_bookmaker_id_bookmaker_match_id', 'bookmaker_id', 'bookmaker_match_id'),
    )


class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, ForeignKey("sport.id", ondelete="CASCADE"))
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)

    sport = relationship("Sport", back_populates="markets")
    match_markets = relationship("MatchMarket", back_populates="market")

    __table_args__ = (
        UniqueConstraint("sport_id", "name", name="uix_sport_market"),
    )


class MatchMarket(Base):
    __tablename__ = "match_market"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(Integer, ForeignKey("match.id", ondelete="CASCADE"))
    market_id = Column(Integer, ForeignKey("market.id", ondelete="CASCADE"))
    line = Column(Float, nullable=True)
    period = Column(String(20), nullable=True)

    match = relationship("Match", back_populates="match_markets")
    market = relationship("Market", back_populates="match_markets")
    outcomes = relationship("Outcome", back_populates="match_market", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_match_market_match_id_market_id", "match_id", "market_id"),
    )


class Outcome(Base):
    __tablename__ = "outcome"

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_market_id = Column(Integer, ForeignKey("match_market.id", ondelete="CASCADE"))
    label = Column(String(30), nullable=False)
    team_id = Column(Integer, ForeignKey("team.id"), nullable=True)
    fair_odds = Column(Float, nullable=True)
    fair_source_bookmaker_id = Column(Integer, ForeignKey("bookmaker.id"), nullable=True)
    fair_computed_at = Column(DateTime, nullable=True)

    match_market = relationship("MatchMarket", back_populates="outcomes")
    bookmaker_odds = relationship("BookmakerOdd", back_populates="outcome", cascade="all, delete-orphan")
    fair_source_bookmaker = relationship("Bookmaker", foreign_keys=[fair_source_bookmaker_id])

    __table_args__ = (
        UniqueConstraint("match_market_id", "label", "team_id", name="uix_outcome"),
    )


class BookmakerOdd(Base):
    __tablename__ = "bookmaker_odd"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmaker_id = Column(Integer, ForeignKey("bookmaker.id", ondelete="CASCADE"))
    outcome_id = Column(Integer, ForeignKey("outcome.id", ondelete="CASCADE"))
    odds = Column(Float, nullable=False)
    edge_odds = Column(Float, nullable=True)
    edge_freebet = Column(Float, nullable=True)
    last_update = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookmaker = relationship("Bookmaker")
    outcome = relationship("Outcome", back_populates="bookmaker_odds")

    __table_args__ = (
        UniqueConstraint("bookmaker_id", "outcome_id", name="uix_bookmaker_outcome"),
        Index("ix_bookmaker_odd_bookmaker_outcome", "bookmaker_id", "outcome_id"),
    )


class Team(Base):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sport_id = Column(Integer, ForeignKey('sport.id', ondelete="CASCADE"))
    name = Column(String(70), nullable=False)

    sport = relationship("Sport", back_populates="teams")
    bookmaker_teams = relationship("BookmakerTeam", back_populates="team", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('sport_id', 'name', name='uix_team_unique'),
        Index('ix_team_sport_id_name', 'sport_id', 'name'),
    )


class BookmakerTeam(Base):
    __tablename__ = 'bookmaker_team'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bookmaker_id = Column(Integer, ForeignKey('bookmaker.id', ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey('team.id', ondelete="CASCADE"))
    bookmaker_team_name = Column(String(60), nullable=False)

    bookmaker = relationship("Bookmaker", back_populates="teams")
    team = relationship("Team", back_populates="bookmaker_teams")

    __table_args__ = (
        UniqueConstraint('bookmaker_id', 'team_id', name='uix_bookmaker_team_unique'),
        Index('ix_bookmaker_team_bookmaker_id_team_id', 'bookmaker_id', 'team_id'),
        Index('ix_bookmaker_team_bookmaker_id_bookmaker_team_name', 'bookmaker_id', 'bookmaker_team_name'),
    )
