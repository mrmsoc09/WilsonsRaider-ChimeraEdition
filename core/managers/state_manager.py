"""State Manager - Persistence Layer for Assessment Data

Manages all database operations for bug bounty assessments.
Version: 2.0.0
"""

import datetime
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

Base = declarative_base()
logger = logging.getLogger(__name__)

class Assessment(Base):
    __tablename__ = 'assessments'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    target = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default='running', index=True)
    description = Column(Text, nullable=True)
    assets = relationship('Asset', back_populates='assessment', cascade='all, delete-orphan')
    findings = relationship('Finding', back_populates='assessment', cascade='all, delete-orphan')

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, default='subdomain', index=True)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='discovered')
    metadata = Column(Text, nullable=True)
    assessment = relationship('Assessment', back_populates='assets')

class Finding(Base):
    __tablename__ = 'findings'
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False, index=True)
    asset_name = Column(String, nullable=False)
    severity = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    proof_of_concept = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    reported = Column(Boolean, default=False)
    assessment = relationship('Assessment', back_populates='findings')

class StateManager:
    """Database manager for assessment persistence."""
    
    def __init__(self, db_uri: str = 'sqlite:///wilsons_raiders.db'):
        self.engine = create_engine(db_uri, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"StateManager initialized with {db_uri}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def create_assessment(self, name: str, target: str, description: str = None) -> Optional[Assessment]:
        """Create new assessment."""
        try:
            with self.get_session() as session:
                assessment = Assessment(name=name, target=target, description=description)
                session.add(assessment)
                session.flush()
                session.refresh(assessment)
                logger.info(f"Created assessment: {name} (id={assessment.id})")
                return assessment
        except Exception as e:
            logger.error(f"Failed to create assessment: {e}")
            return None
    
    def get_assessment(self, assessment_id: int) -> Optional[Assessment]:
        """Get assessment by ID."""
        try:
            with self.get_session() as session:
                return session.query(Assessment).filter_by(id=assessment_id).first()
        except Exception as e:
            logger.error(f"Failed to get assessment: {e}")
            return None
    
    def list_assessments(self, status: str = None) -> List[Assessment]:
        """List all assessments, optionally filtered by status."""
        try:
            with self.get_session() as session:
                query = session.query(Assessment)
                if status:
                    query = query.filter_by(status=status)
                return query.order_by(Assessment.start_time.desc()).all()
        except Exception as e:
            logger.error(f"Failed to list assessments: {e}")
            return []
    
    def update_assessment_status(self, assessment_id: int, status: str) -> bool:
        """Update assessment status."""
        try:
            with self.get_session() as session:
                assessment = session.query(Assessment).filter_by(id=assessment_id).first()
                if assessment:
                    assessment.status = status
                    if status == 'completed':
                        assessment.end_time = datetime.datetime.utcnow()
                    logger.info(f"Updated assessment {assessment_id} status to {status}")
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update assessment status: {e}")
            return False
    
    def add_assets(self, assessment_id: int, asset_names: List[str], asset_type: str = 'subdomain') -> bool:
        """Add multiple assets to assessment."""
        try:
            with self.get_session() as session:
                assessment = session.query(Assessment).filter_by(id=assessment_id).first()
                if not assessment:
                    return False
                
                for asset_name in asset_names:
                    asset = Asset(name=asset_name, type=asset_type)
                    assessment.assets.append(asset)
                
                logger.info(f"Added {len(asset_names)} assets to assessment {assessment_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to add assets: {e}")
            return False
    
    def add_finding(self, assessment_id: int, asset_name: str, severity: str, 
                   title: str, description: str, poc: str = None, remediation: str = None) -> Optional[Finding]:
        """Add vulnerability finding to assessment."""
        try:
            with self.get_session() as session:
                finding = Finding(
                    assessment_id=assessment_id,
                    asset_name=asset_name,
                    severity=severity,
                    title=title,
                    description=description,
                    proof_of_concept=poc,
                    remediation=remediation
                )
                session.add(finding)
                session.flush()
                logger.info(f"Added {severity} finding to assessment {assessment_id}: {title}")
                return finding
        except Exception as e:
            logger.error(f"Failed to add finding: {e}")
            return None
    
    def get_findings(self, assessment_id: int, severity: str = None) -> List[Finding]:
        """Get findings for assessment, optionally filtered by severity."""
        try:
            with self.get_session() as session:
                query = session.query(Finding).filter_by(assessment_id=assessment_id)
                if severity:
                    query = query.filter_by(severity=severity)
                return query.order_by(Finding.discovered_at.desc()).all()
        except Exception as e:
            logger.error(f"Failed to get findings: {e}")
            return []
