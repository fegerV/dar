"""
Wallet and Ledger models for tracking user balance and transactions.

Following the ledger pattern: all money, bonuses, orders and generation states 
are stored in PostgreSQL. Balance is computed from transactions.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import String, Boolean, DateTime, Integer, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class TransactionType(str, Enum):
    """Transaction types."""

    WELCOME_BONUS = "welcome_bonus"
    PROMOTION = "promotion"
    REFUND = "refund"
    GENERATION_PAYMENT = "generation_payment"
    ORDER_PAYMENT = "order_payment"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class WalletAccount(Base):
    """User wallet account."""

    __tablename__ = "wallet_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    transactions: Mapped[list["WalletTransaction"]] = relationship(
        "WalletTransaction", back_populates="account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WalletAccount(id={self.id}, user_id={self.user_id})>"


class WalletTransaction(Base):
    """Wallet transaction ledger entry.

    This is the source of truth for all user balances.
    """

    __tablename__ = "wallet_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wallet_accounts.id", ondelete="CASCADE"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RUB")
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(50), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # e.g., 'generation', 'order'
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    balance_after: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    account: Mapped["WalletAccount"] = relationship(
        "WalletAccount", back_populates="transactions"
    )

    def __repr__(self) -> str:
        return f"<WalletTransaction(id={self.id}, amount={self.amount}, type={self.transaction_type})>"


class BonusRule(Base):
    """Bonus rules configuration."""

    __tablename__ = "bonus_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bonus_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    bonus_type: Mapped[TransactionType] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    conditions: Mapped[dict | None] = mapped_column(
        String(1000), nullable=True
    )  # JSON-like conditions
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BonusRule(id={self.id}, name={self.name})>"
