import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=True)
    credits = Column(Integer, default=3)
    is_admin = Column(Integer, default=0)
    plan = Column(String, default="free")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    tests = relationship("Test", back_populates="user")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="tests")
    persona_results = relationship("PersonaResult", back_populates="test", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="test", cascade="all, delete-orphan")
    ux_score = relationship("UXScore", back_populates="test", uselist=False, cascade="all, delete-orphan")

class PersonaResult(Base):
    __tablename__ = "persona_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    persona_name = Column(String)
    status = Column(String, default="pending")
    screenshot_paths = Column(JSON, default=list)
    video_path = Column(String, nullable=True)
    navigation_path = Column(JSON, default=list)
    issues_found = Column(JSON, default=list)
    load_times = Column(JSON, default=dict)
    persona_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    test = relationship("Test", back_populates="persona_results")

class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    persona_name = Column(String)
    type = Column(String)
    description = Column(Text)
    severity = Column(String)
    element = Column(String, nullable=True)
    url = Column(String, nullable=True)
    suggestion = Column(Text, nullable=True)
    test = relationship("Test", back_populates="issues")

class UXScore(Base):
    __tablename__ = "ux_scores"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    overall_score = Column(Float)
    navigation_score = Column(Float)
    clarity_score = Column(Float)
    speed_score = Column(Float)
    mobile_score = Column(Float)
    content_score = Column(Float)
    summary = Column(Text)
    breakdown = Column(JSON, default=dict)
    test = relationship("Test", back_populates="ux_score")
