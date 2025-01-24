from sqlalchemy import BigInteger,cast,desc,or_
import sys
from database import get_db
from main import db_dependency
from models import *
import pytest

@pytest.fixture
def db():
    return next(get_db())


def test_true_or_false():
	assert 3==3

def test_player_fetch(db:db_dependency):
	query=(
		db.query(AtpPlayers)
		.filter(AtpPlayers.
		  player_id==100001)
		  .first()
	)

	assert query.name_full=="Gardnar Mulloy"

def test_matches_fetch(db:db_dependency):
    query = (
        db.query(
            AtpSingles.match_id,
            AtpSingles.match_num,
            AtpSingles.winner_id,
            AtpSingles.loser_id,
            AtpSingles.score,
            AtpSingles.round,
            AtpSingles.minutes,
            AtpPlayers.name_full.label('winner_name'),
            TotalTourneys.tourney_name.label('tournament_name')
        )
        .join(
            AtpPlayers,
            cast(AtpSingles.winner_id, BigInteger) == cast(AtpPlayers.player_id, BigInteger)
        )
        .join(
            TotalTourneys,
            AtpSingles.tourney_id == TotalTourneys.tourney_name_date_matches
        )
        .filter(
            or_(
                (cast(AtpSingles.winner_id, BigInteger) == 100581) & 
                (cast(AtpSingles.loser_id, BigInteger) == 100437),
                (cast(AtpSingles.winner_id, BigInteger) == 100437) & 
                (cast(AtpSingles.loser_id, BigInteger) == 100581)
            )
        )
        .count()
    		)
    assert query==14



