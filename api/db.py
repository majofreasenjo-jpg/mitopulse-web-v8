import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mitopulse_v10.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class UploadRun(Base):
    __tablename__ = "upload_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False)
    client_type = Column(String, nullable=False)
    client_size = Column(String, nullable=False, default="custom")
    source_kind = Column(String, nullable=False)
    folder_path = Column(String, nullable=False)
    summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class CaseRecord(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False)
    run_id = Column(Integer, nullable=False)
    case_title = Column(String, nullable=False)
    status = Column(String, default="open")
    details_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tenant_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    payload_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS upload_runs CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS cases CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS audit_logs CASCADE;"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
