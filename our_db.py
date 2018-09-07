
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:',  echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Member(Base):
        __tablename__ = 'members'

        id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
        user = Column(String)
        ign = Column(String)
        planet = Column(String)
        quest = Column(String)
        def __repr__(self):
            return "<Member(name={0}, fullname={1}, password={2})>".format(
                                                                                                            self.user, self.ign, self.planet, self.quest)

Base.metadata.create_all(engine)

