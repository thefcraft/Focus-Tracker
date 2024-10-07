from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta, timezone  
from typing import List

DATABASE_URL = 'sqlite:///activity_log.db' # Define the database URL
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

    
class Activity(Base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    program_name = Column(String)
    window_title = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    duration = Column(Integer)  # duration in seconds
    endtimestamp = Column(DateTime)
    
    def __repr__(self):
        return f'Activity({self.program_name})'

# Create the database and tables
Base.metadata.create_all(engine)
def add_activity(program_name, window_title, duration):
    session = Session()
    endtimestamp = datetime.now(timezone.utc) + timedelta(seconds=duration)  # Use timezone-aware datetime
    new_activity = Activity(program_name=program_name, window_title=window_title, duration=duration, endtimestamp=endtimestamp)
    session.add(new_activity)
    session.commit()
    session.close()
    
def filter_by(day=None, month=None, year=None):
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
    
    session = Session()
    results = session.query(Activity).filter(*filters).all()
    session.close()
    return results    

# Example usage
if __name__ == "__main__":
    # Add a program
    # add_activity("My Program", "My Window", 120)  # Duration of 120 seconds

    # Filter programs by specific day
    print(filter_by(3, 10, 2024))
    print(filter_by(month=10, year=2024))
    print(filter_by(year=2024))
    print(filter_by(month=10))
