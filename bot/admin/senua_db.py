import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:wastedPenguin27.@localhost:5432/discordis',  echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, Sequence('users_id_seq'), primary_key=True)
        user = Column(String)
        ign = Column(String)
        game = Column(String)

        def __repr__(self):
            return '<User: {0}, IGN:{1}, Game:{2})>'.format(self.user, self.ign, self.game)

class Clan(Base):
        __tablename__ = 'clans'

        id = Column(Integer, Sequence('clan_id_seq'), primary_key=True)
        clan_name = Column(String)
        clan_tier = Column(String)
        clan_level = Column(String)
        clan_research = Column(String)
        clan_resources = Column(String)
        clan_priority = Column(String)
        clan_events = Column(String)        

        def __repr__(self):
            return "<Clan #{5}(Clan Name={0}, Clan Tier={1}, Clan Level={2}, Clan Research={3}, Clan Resources={4}, Clan Priority={6})>".format(
                                                                                                self.clan_name, self.clan_tier, self.clan_level, self.clan_research, self.clan_resources, self.id)

Base.metadata.create_all(engine)
