import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    target = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='running')
    assets = relationship('Asset', back_populates='assessment')

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    name = Column(String, nullable=False)
    type = Column(String, default='subdomain')
    assessment = relationship('Assessment', back_populates='assets')

class StateManager:
    def __init__(self, db_uri='sqlite:///wilsons_raiders.db'):
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def create_assessment(self, name, target):
        session = self.get_session()
        try:
            new_assessment = Assessment(name=name, target=target)
            session.add(new_assessment)
            session.commit()
            # This is the crucial fix: load the ID before closing the session.
            session.refresh(new_assessment)
            return new_assessment
        finally:
            session.close()

    def get_assessment(self, assessment_id):
        session = self.get_session()
        try:
            return session.query(Assessment).filter_by(id=assessment_id).first()
        finally:
            session.close()
    
    def add_assets(self, assessment_id, asset_names):
        session = self.get_session()
        try:
            assessment = session.query(Assessment).filter_by(id=assessment_id).first()
            if assessment:
                for asset_name in asset_names:
                    new_asset = Asset(name=asset_name)
                    assessment.assets.append(new_asset)
                session.commit()
        finally:
            session.close()
