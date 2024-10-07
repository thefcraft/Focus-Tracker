from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timedelta, timezone  
from typing import List, Optional, NewType
import os



Base = declarative_base()

Duration = NewType('Duration', int) # Duration in seconds

class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    program_name = Column(String)
    window_title = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    duration = Column(Integer, default=0)  # duration in seconds
    endtimestamp = Column(DateTime)
    
    def __repr__(self):
        return f'Activity({self.program_name})'

# class Todo(Base): ...
# class Note(Base): ...
# class Goal(Base): ...

class database:
    # this should give high level abstraction to the database interface
    def __init__(self, name="activity_log.db", dir=os.path.dirname(__file__)): 
        self.FILE_PATH = os.path.join(dir, name)
        self.DATABASE_URL = f'sqlite:///{self.FILE_PATH}' # Define the database URL
        self.engine = create_engine(self.DATABASE_URL, echo=False)
        self._Session: sessionmaker[Session] = sessionmaker(bind=self.engine)
        self.create_all()
    def migrate(self): ...
    def create_all(self):
        # init_db
        if not os.path.exists(self.FILE_PATH):
            # Create the database and tables
            Base.metadata.create_all(self.engine)
            print("Database and tables created!")
    def delete_all(self):
        # delete all tables and create new tables 
        os.remove(self.FILE_PATH)
        self.create_all()
    def new_session(self): return self._Session()
    @staticmethod
    def _get_filters(day:Optional[int]=None, month:Optional[int]=None, year:Optional[int]=None):
        now = datetime.now(timezone.utc)
        _filter_by = 0 # ["day", "month", "year"]

        # (day=None, month=None, year=None) => (day=now, month=now, year=now)
        if day is None and month is None and year is None:
            day = now.day
            month = now.month
            year = now.year
        # (day=d, month=None, year=None) => (day=d, month=now, year=now)
        elif day is not None and month is None and year is None:
            month = now.month
            year = now.year
        # (day=d, month=m, year=None) => (day=d, month=m, year=now)        
        elif day is not None and month is not None and year is None:
            year = now.year
        # (day=None, month=m, year=y) => (day=None, month=m, year=y).all()
        elif day is None and month is not None and year is not None:
            _filter_by = 1
        # (day=None, month=m, year=None) => (day=None, month=m, year=now).all()
        elif day is None and month is not None and year is None:
            year = now.year
            _filter_by = 1
        # (day=None, month=None, year=None) => (day=None, month=None, year=y).all()
        elif day is None and month is None and year is not None:
            _filter_by = 2

        # Build the filters
        filters = [(
                func.extract('year', Activity.timestamp) == year,
                func.extract('month', Activity.timestamp) == month,
                func.extract('day', Activity.timestamp) == day
            ), (
                func.extract('year', Activity.timestamp) == year,
                func.extract('month', Activity.timestamp) == month
            ), (
                func.extract('year', Activity.timestamp) == year, 
        )][_filter_by]
        return filters
    
    def add_activity(self, program_name:str, window_title:str, duration:Duration, session:Optional[Session]=None):
        if session is not None:
            endtimestamp = datetime.now(timezone.utc) + timedelta(seconds=duration)  # Use timezone-aware datetime
            new_activity = Activity(program_name=program_name, window_title=window_title, duration=duration, endtimestamp=endtimestamp)    
            session.add(new_activity)
            return None
        
        session = self.new_session()
        endtimestamp = datetime.now(timezone.utc) + timedelta(seconds=duration)  # Use timezone-aware datetime
        new_activity = Activity(program_name=program_name, window_title=window_title, duration=duration, endtimestamp=endtimestamp)
        session.add(new_activity)
        session.commit()
        session.close()
    
    def filter_by(self, day:Optional[int]=None, month:Optional[int]=None, year:Optional[int]=None, session:Optional[Session]=None)->List[Activity]:
        if session is not None:
            results = session.query(Activity).filter(*self._get_filters(day, month, year)).all()
            return results    
        session = self.new_session()
        results = session.query(Activity).filter(*self._get_filters(day, month, year)).all()
        session.close()
        return results    