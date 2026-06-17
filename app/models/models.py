from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    stars_balance = Column(Float, default=0)
    total_earned = Column(Float, default=0)
    cases_opened = Column(Integer, default=0)
    referrer_id = Column(BigInteger, nullable=True)
    referral_count = Column(Integer, default=0)
    referral_earnings = Column(Float, default=0)
    level = Column(Integer, default=1)
    rank = Column(String(50), default='Bronze')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    case_openings = relationship('CaseOpening', back_populates='user', foreign_keys='CaseOpening.user_id')
    referrals = relationship('Referral', back_populates='referrer', foreign_keys='Referral.referrer_id')


class CaseOpening(Base):
    """Case opening record"""
    __tablename__ = 'case_openings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    case_type = Column(String(50), nullable=False)
    amount_spent = Column(Float, nullable=False)
    reward = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)  # reward - amount_spent
    opened_at = Column(DateTime, default=datetime.utcnow, index=True)
    transaction_id = Column(String(255), unique=True, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='case_openings', foreign_keys=[user_id])


class Referral(Base):
    """Referral tracking"""
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    referee_id = Column(BigInteger, nullable=False, index=True)
    commission = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    referrer = relationship('User', back_populates='referrals', foreign_keys=[referrer_id])


class Transaction(Base):
    """Transaction history"""
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False)  # case_opened, referral_bonus, etc.
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    status = Column(String(50), default='completed')  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    meta = Column('metadata', String, nullable=True)  # JSON metadata


class Leaderboard(Base):
    """Leaderboard snapshot"""
    __tablename__ = 'leaderboard'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, unique=True, index=True)
    rank = Column(Integer, nullable=False)
    total_earned = Column(Float, default=0)
    cases_opened = Column(Integer, default=0)
    username = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
