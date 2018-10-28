
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://postgres:wastedPenguin27.@localhost:5432/senua_db',  echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Member(Base):
        __tablename__ = 'members'

        id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
        user = Column(String)
        ign = Column(String)
        planet = Column(String)
        quest = Column(String)
        priority = Column(String)
        syndicate = Column(String)
        def __repr__(self):
            return "<Member #{4}(User={0}, IGN={1}, Planet={2}, Quest={3}, Priority={5}, Syndicate={6})>".format(
                                                                        self.user, self.ign, self.planet, self.quest, self.id, self.priority, self.syndicate)

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


class Alliance(Base):
        __tablename__ = 'alliances'

        id = Column(Integer, Sequence('alliance_id_seq'), primary_key=True)
        member_count = Column(String)
        clan_count = Column(String)
        alliance_events = Column(String)

        def __repr__(self):
            return "<Alliance(Member Count={0}, Clan Count={1}, Alliance Events={2})>".format(
                                                                    self.member_count, self.clan_count, self.alliance_events)
        

Base.metadata.create_all(engine)

