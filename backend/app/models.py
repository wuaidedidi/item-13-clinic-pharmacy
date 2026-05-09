from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="enabled")


class Supplier(Base, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    contact_person: Mapped[str] = mapped_column(String(64), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)
    email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    supply_scope: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")


class Medicine(Base, TimestampMixin):
    __tablename__ = "medicines"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    specification: Mapped[str] = mapped_column(String(128), nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    current_stock: Mapped[int] = mapped_column(nullable=False, default=0)
    safety_stock: Mapped[int] = mapped_column(nullable=False, default=0)
    selling_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    purchase_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    expiry_warning_days: Mapped[int] = mapped_column(nullable=False, default=90)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")

    supplier: Mapped["Supplier"] = relationship("Supplier")


class MedicineBatch(Base, TimestampMixin):
    __tablename__ = "medicine_batches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    batch_no: Mapped[str] = mapped_column(String(64), nullable=False)
    inbound_order_no: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    remaining_quantity: Mapped[int] = mapped_column(nullable=False)
    production_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    inbound_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="available")

    medicine: Mapped["Medicine"] = relationship("Medicine")


class InboundOrder(Base, TimestampMixin):
    __tablename__ = "inbound_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("medicine_batches.id", ondelete="SET NULL"), nullable=True)
    batch_no: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    purchase_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    received_by: Mapped[str] = mapped_column(String(64), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="completed")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class PrescriptionIssue(Base, TimestampMixin):
    __tablename__ = "prescription_issues"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    issue_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    patient_name: Mapped[str] = mapped_column(String(64), nullable=False)
    doctor_name: Mapped[str] = mapped_column(String(64), nullable=False)
    issued_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="completed")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class PrescriptionIssueItem(Base):
    __tablename__ = "prescription_issue_items"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("prescription_issues.id", ondelete="CASCADE"), nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    batch_id: Mapped[int | None] = mapped_column(ForeignKey("medicine_batches.id", ondelete="SET NULL"), nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.00)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class StockCount(Base, TimestampMixin):
    __tablename__ = "stock_counts"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    count_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    system_quantity: Mapped[int] = mapped_column(nullable=False)
    counted_quantity: Mapped[int] = mapped_column(nullable=False)
    difference_qty: Mapped[int] = mapped_column(nullable=False)
    counted_by: Mapped[str] = mapped_column(String(64), nullable=False)
    counted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="draft")
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class AdjustmentOrder(Base, TimestampMixin):
    __tablename__ = "adjustment_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    count_id: Mapped[int | None] = mapped_column(ForeignKey("stock_counts.id", ondelete="SET NULL"), nullable=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    system_quantity: Mapped[int] = mapped_column(nullable=False)
    counted_quantity: Mapped[int] = mapped_column(nullable=False)
    difference_qty: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ExpiryWarning(Base):
    __tablename__ = "expiry_warnings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    batch_id: Mapped[int] = mapped_column(ForeignKey("medicine_batches.id", ondelete="CASCADE"), nullable=False)
    warning_type: Mapped[str] = mapped_column(String(32), nullable=False)
    days_left: Mapped[int] = mapped_column(nullable=False)
    warning_level: Mapped[str] = mapped_column(String(16), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")


class PurchaseOrder(Base, TimestampMixin):
    __tablename__ = "purchase_orders"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    medicine_id: Mapped[int] = mapped_column(ForeignKey("medicines.id", ondelete="RESTRICT"), nullable=False)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    requested_qty: Mapped[int] = mapped_column(nullable=False)
    suggested_qty: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
