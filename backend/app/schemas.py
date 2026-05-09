from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenData(BaseModel):
    sub: str


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=64)
    password: str = Field(min_length=6, max_length=64)
    nickname: str = Field(min_length=2, max_length=64)
    phone: Optional[str] = Field(default=None, max_length=32)
    email: Optional[EmailStr] = None


class PasswordChangeRequest(BaseModel):
    old_password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)


class ProfileUpdateRequest(BaseModel):
    nickname: str = Field(min_length=2, max_length=64)
    phone: Optional[str] = Field(default=None, max_length=32)
    email: Optional[EmailStr] = None


class UserOut(BaseSchema):
    id: int
    username: str
    nickname: str
    role: str
    phone: Optional[str]
    email: Optional[str]
    status: str
    created_at: datetime


class LoginResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SupplierBase(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    contact_person: str = Field(min_length=2, max_length=64)
    phone: str = Field(min_length=3, max_length=32)
    email: Optional[EmailStr] = None
    address: str = Field(min_length=2, max_length=255)
    supply_scope: str = Field(min_length=2, max_length=255)
    status: str = Field(default="active", max_length=16)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(BaseSchema):
    id: int
    name: str
    contact_person: str
    phone: str
    email: Optional[str]
    address: str
    supply_scope: str
    status: str
    created_at: datetime


class MedicineBase(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=128)
    specification: str = Field(min_length=1, max_length=128)
    unit: str = Field(min_length=1, max_length=32)
    category: str = Field(min_length=1, max_length=64)
    current_stock: int = Field(ge=0)
    safety_stock: int = Field(ge=0)
    selling_price: Decimal = Field(ge=0)
    purchase_price: Decimal = Field(ge=0)
    expiry_warning_days: int = Field(ge=1, le=3650)
    supplier_id: Optional[int] = None
    location: Optional[str] = Field(default=None, max_length=128)
    status: str = Field(default="active", max_length=16)


class MedicineCreate(MedicineBase):
    pass


class MedicineUpdate(MedicineBase):
    pass


class MedicineOut(BaseSchema):
    id: int
    code: str
    name: str
    specification: str
    unit: str
    category: str
    current_stock: int
    safety_stock: int
    selling_price: Decimal
    purchase_price: Decimal
    expiry_warning_days: int
    supplier_id: Optional[int]
    location: Optional[str]
    status: str
    created_at: datetime


class BatchCreate(BaseModel):
    medicine_id: int
    supplier_id: Optional[int] = None
    batch_no: str = Field(min_length=2, max_length=64)
    quantity: int = Field(gt=0)
    purchase_price: Decimal = Field(ge=0)
    production_date: Optional[date] = None
    expiry_date: date
    location: Optional[str] = Field(default=None, max_length=128)
    remark: Optional[str] = Field(default=None, max_length=255)


class InboundCreate(BatchCreate):
    received_by: str = Field(min_length=2, max_length=64)


class InboundOut(BaseSchema):
    id: int
    order_no: str
    medicine_id: int
    supplier_id: Optional[int]
    batch_id: Optional[int]
    batch_no: str
    quantity: int
    purchase_price: Decimal
    received_by: str
    received_at: datetime
    status: str
    remark: Optional[str]


class PrescriptionIssueCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=64)
    doctor_name: str = Field(min_length=2, max_length=64)
    medicine_id: int
    quantity: int = Field(gt=0)
    remark: Optional[str] = Field(default=None, max_length=255)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)


class PrescriptionIssueOut(BaseSchema):
    id: int
    issue_no: str
    patient_name: str
    doctor_name: str
    issued_by: int
    issued_at: datetime
    total_amount: Decimal
    status: str
    remark: Optional[str]


class StockCountCreate(BaseModel):
    medicine_id: int
    counted_quantity: int = Field(ge=0)
    counted_by: str = Field(min_length=2, max_length=64)
    remark: Optional[str] = Field(default=None, max_length=255)


class StockCountOut(BaseSchema):
    id: int
    count_no: str
    medicine_id: int
    system_quantity: int
    counted_quantity: int
    difference_qty: int
    counted_by: str
    counted_at: datetime
    status: str
    remark: Optional[str]


class AdjustmentCreate(BaseModel):
    count_id: Optional[int] = None
    medicine_id: int
    system_quantity: int
    counted_quantity: int
    difference_qty: int
    reason: str = Field(min_length=2, max_length=255)
    created_by: int
    remark: Optional[str] = Field(default=None, max_length=255)


class AdjustmentOut(BaseSchema):
    id: int
    order_no: str
    count_id: Optional[int]
    medicine_id: int
    system_quantity: int
    counted_quantity: int
    difference_qty: int
    reason: str
    status: str
    created_by: int
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    remark: Optional[str]


class WarningOut(BaseSchema):
    id: int
    medicine_id: int
    batch_id: int
    warning_type: str
    days_left: int
    warning_level: str
    generated_at: datetime
    status: str


class PurchaseOrderCreate(BaseModel):
    medicine_id: int
    supplier_id: int
    requested_qty: int = Field(gt=0)
    suggested_qty: int = Field(gt=0)
    reason: str = Field(min_length=2, max_length=255)
    created_by: int
    remark: Optional[str] = Field(default=None, max_length=255)


class PurchaseOrderOut(BaseSchema):
    id: int
    order_no: str
    medicine_id: int
    supplier_id: int
    requested_qty: int
    suggested_qty: int
    reason: str
    status: str
    created_by: int
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    remark: Optional[str]


class DashboardSummary(BaseModel):
    expiring_batch_count: int
    turnover_rate: float
    today_issue_amount: Decimal
    shortage_medicine_count: int
    pending_purchase_count: int
    expiring_batches: list[dict[str, Any]]
    shortage_items: list[dict[str, Any]]
    pending_adjustments: list[dict[str, Any]]
    recent_inbounds: list[dict[str, Any]]
    recent_issues: list[dict[str, Any]]
    role_tiles: list[dict[str, Any]]
