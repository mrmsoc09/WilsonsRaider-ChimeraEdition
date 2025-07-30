import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    target = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    assets = relationship('Asset', back_populates='assessment')
    vulnerabilities = relationship('Vulnerability', back_populates='assessment')

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    assessment = relationship('Assessment', back_populates='assets')
    hostname = Column(String)
    ip_address = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    is_alive = Column(Boolean, default=False)

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    assessment = relationship('Assessment', back_populates='vulnerabilities')
    name = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String)
    tool = Column(String)
    reproduction_script = Column(Text)

class StateManager:
    def __init__(self, db_uri='sqlite:///wilsons_raiders.db'):
        """
        Initializes the StateManager.
        db_uri can be a sqlite connection string (default) or a postgresql connection string.
        e.g., 'postgresql://user:password@host:port/dbname'
        """
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def add_assessment(self, target):
        session = self.get_session()
        assessment = Assessment(target=target)
        session.add(assessment)
        session.commit()
        session.close()
        return assessment.id
