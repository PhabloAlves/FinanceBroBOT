from sqlalchemy import BigInteger, Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    telegram_user_id = Column(BigInteger, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MonthlyIncome(Base):
    __tablename__ = "monthly_income"
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, ForeignKey("users.telegram_user_id"), nullable=False)
    month = Column(String(7), nullable=False)  # MM/YYYY
    amount = Column(Numeric(12, 2), nullable=False, default=0)
    __table_args__ = (UniqueConstraint("telegram_user_id", "month"),)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, ForeignKey("users.telegram_user_id"), nullable=False)
    data = Column(String(10), nullable=False)  
    categoria = Column(String(100))
    tipo = Column(String(10), nullable=False)  
    descricao = Column(String(255))
    valor = Column(Numeric(12, 2), nullable=False)
    forma_pagamento = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())