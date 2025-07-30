import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()

class Program(Base):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    assessments = relationship("Assessment", back_populates="program")

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey('programs.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    program = relationship("Program", back_populates="assessments")
    assets = relationship("Asset", back_populates="assessment")

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    name = Column(String, nullable=False)
    asset_type = Column(String, default='domain')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    assessment = relationship("Assessment", back_populates="assets")
    vulnerabilities = relationship("Vulnerability", back_populates="asset")

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    name = Column(String, nullable=False)
    severity = Column(String)
    description = Column(Text)
    raw_finding = Column(Text)
    is_validated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    asset = relationship("Asset", back_populates="vulnerabilities")

class StateManager:
    """Manages the state of the application using a SQLite database."""

    def __init__(self, db_path: str = 'raider_state.db'):
        try:
            self.engine = create_engine(f'sqlite:///{db_path}')
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(f"[ERROR] Failed to initialize database: {e}")
            raise

    def get_session(self):
        return self.Session()

    def create_assessment(self, program_name: str, domain: str) -> Assessment:
        session = self.get_session()
        try:
            program = session.query(Program).filter_by(name=program_name).first()
            if not program:
                program = Program(name=program_name)
                session.add(program)
                session.flush()

            assessment = Assessment(program_id=program.id)
            session.add(assessment)
            session.flush()
            
            asset = Asset(name=domain, assessment_id=assessment.id)
            session.add(asset)
            session.commit()
            return assessment
        except SQLAlchemyError as e:
            session.rollback()
            print(f"[ERROR] Could not create assessment: {e}")
            raise
        finally:
            session.close()
            
    def add_vulnerabilities(self, assessment_id: str, vulnerabilities: list):
        pass # Placeholder for adding vulns

    def get_assessment(self, assessment_id: int):
        pass # Placeholder for getting assessment details
