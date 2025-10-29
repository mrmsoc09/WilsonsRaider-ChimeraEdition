<<<<<<< HEAD
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

import sqlcipher3
from core.config_manager import ConfigManager
=======
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
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

Base = declarative_base()
logger = logging.getLogger(__name__)

class Program(Base):
    __tablename__ = 'programs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    assessments = relationship("Assessment", back_populates="program")

class Assessment(Base):
    __tablename__ = 'assessments'
<<<<<<< HEAD
    id = Column(Integer, primary_key=True, autoincrement=True)
    program_id = Column(Integer, ForeignKey('programs.id'))
    target = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='running')
    program = relationship("Program", back_populates="assessments")
    assets = relationship("Asset", back_populates="assessment")
    vulnerabilities = relationship("Vulnerability", back_populates="assessment")
=======
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    target = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default='running', index=True)
    description = Column(Text, nullable=True)
    assets = relationship('Asset', back_populates='assessment', cascade='all, delete-orphan')
    findings = relationship('Finding', back_populates='assessment', cascade='all, delete-orphan')
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
<<<<<<< HEAD
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    name = Column(String, nullable=False) # e.g., subdomain, IP
    asset_type = Column(String, default='domain') # e.g., domain, ip, mobile_app
    hostname = Column(String)
    ip_address = Column(String)
    port = Column(Integer)
    protocol = Column(String)
    is_alive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    assessment = relationship("Assessment", back_populates="assets")
    vulnerabilities = relationship("Vulnerability", back_populates="asset")

class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    assessment_id = Column(Integer, ForeignKey('assessments.id'))
    name = Column(String, nullable=False)
    severity = Column(String)
    description = Column(Text)
    raw_finding = Column(Text)
    tool = Column(String)
    is_validated = Column(Boolean, default=False)
    reproduction_script = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    asset = relationship("Asset", back_populates="vulnerabilities")
    assessment = relationship("Assessment", back_populates="vulnerabilities")

=======
    assessment_id = Column(Integer, ForeignKey('assessments.id'), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    type = Column(String, default='subdomain', index=True)
    discovered_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default='discovered')
    metadata = Column(Text, nullable=True)
    assessment = relationship('Assessment', back_populates='assets')
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4

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
<<<<<<< HEAD
    """
    Manages the state of the application using a database.
    This is the canonical, unified version.
    """
    def __init__(self):
        """
        Initializes the StateManager with database encryption using the correct dialect and URI format.
        """
        self.config = ConfigManager()
        db_uri = self.config.get('database.uri')

        db_key = os.getenv('DB_ENCRYPTION_KEY')
        if not db_key:
            raise ValueError("DB_ENCRYPTION_KEY environment variable not set. Cannot operate on encrypted database.")

        try:
            # Ensure we have an absolute path for the database file.
            db_filename = db_uri.replace('sqlite:///', '')
            db_abs_path = os.path.abspath(db_filename)

            # Use the standard sqlite:/// URI format, but provide a custom creator function
            # that uses sqlcipher3.connect and passes the passphrase.
            def creator():
                conn = sqlcipher3.connect(db_abs_path)
                conn.execute(f'PRAGMA key = "{db_key}"')
                return conn

            self.engine = create_engine(f'sqlite:///{db_abs_path}', creator=creator)

            # Test the connection and key by executing a simple statement.
            with self.engine.connect() as connection:
                connection.execute(func.now())

            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
        except Exception as e:
            print(f"[ERROR] Failed to initialize encrypted database: {e}")
            raise

    def get_session(self):
        return self.Session()

    def create_assessment(self, program_name: str, target: str) -> Assessment:
        session = self.get_session()
        try:
            program = session.query(Program).filter_by(name=program_name).first()
            if not program:
                program = Program(name=program_name)
                session.add(program)

            assessment = Assessment(program_id=program.id, target=target)
            session.add(assessment)
            session.commit()
            return assessment.id
        except SQLAlchemyError as e:
            session.rollback()
            print(f"[ERROR] Could not create assessment: {e}")
            raise
        finally:
            session.close()

    def add_assets(self, assessment_id: int, asset_data: list[dict]):
        session = self.get_session()
        try:
            for data in asset_data:
                new_asset = Asset(assessment_id=assessment_id, **data)
                session.add(new_asset)
            session.commit()
        finally:
            session.close()

    def add_vulnerability(self, assessment_id: int, asset_id: int, vuln_data: dict):
        session = self.get_session()
        try:
            new_vuln = Vulnerability(
                assessment_id=assessment_id,
                asset_id=asset_id,
                **vuln_data
            )
            session.add(new_vuln)
            session.commit()
        finally:
            session.close()

    def get_vulnerabilities_for_assessment(self, assessment_id: int):
        session = self.get_session()
        try:
            return session.query(Vulnerability).filter_by(assessment_id=assessment_id).all()
        finally:
            session.close()
=======
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
>>>>>>> a6084cc3ed82e7829e4008fdba7650ce580d27d4
