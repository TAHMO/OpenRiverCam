from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from models.base import Base

# TODO: Remove hardcoded connection URI.
engine = create_engine('postgresql://postgres:password@db:5432/openrivercam')


from models import bathymetry
from models import camera
from models import movie
from models import polygon
from models import site

Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db = scoped_session(DBSession)