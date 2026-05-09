from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessError
from app.models import AdjustmentOrder, InboundOrder, Medicine, MedicineBatch, PrescriptionIssue, PrescriptionIssueItem, StockCount, Supplier
from app.schemas import BatchCreate, InboundCreate, MedicineCreate, PrescriptionIssueCreate, PurchaseOrderCreate, StockCountCreate
from app.services.common import generate_no


def list_medicines(db: Session):
    return db.query(Medicine).order_by(Medicine.updated_at.desc()).all()


def create_medicine(db: Session, payload: MedicineCreate) -> Medicine:
    exists = db.query(Medicine).filter(Medicine.code == payload.code).one_or_none()
    if exists:
        raise BusinessError(409, "药品编码已存在")
    medicine = Medicine(**payload.model_dump())
    db.add(medicine)
    db.commit()
    db.refresh(medicine)
    return medicine


def update_medicine(db: Session, medicine: Medicine, payload: MedicineCreate) -> Medicine:
    for key, value in payload.model_dump().items():
        setattr(medicine, key, value)
    db.commit()
    db.refresh(medicine)
    return medicine


def delete_medicine(db: Session, medicine: Medicine) -> None:
    has_batches = db.query(MedicineBatch.id).filter(MedicineBatch.medicine_id == medicine.id).first()
    if has_batches:
        raise BusinessError(400, "该药品已有批次记录，无法删除")
    db.delete(medicine)
    db.commit()


def create_inbound(db: Session, payload: InboundCreate) -> InboundOrder:
    medicine = db.get(Medicine, payload.medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    supplier = db.get(Supplier, payload.supplier_id) if payload.supplier_id else None
    order_no = f"{generate_no('IN')}{str(int(datetime.now().timestamp()))[-4:]}"
    batch = MedicineBatch(
        medicine_id=medicine.id,
        supplier_id=supplier.id if supplier else None,
        batch_no=payload.batch_no,
        inbound_order_no=order_no,
        quantity=payload.quantity,
        remaining_quantity=payload.quantity,
        production_date=payload.production_date,
        expiry_date=payload.expiry_date,
        inbound_date=datetime.now(),
        location=payload.location,
        remark=payload.remark,
        status="available",
    )
    medicine.current_stock += payload.quantity
    db.add(batch)
    db.flush()
    inbound = InboundOrder(
        order_no=order_no,
        medicine_id=medicine.id,
        supplier_id=supplier.id if supplier else None,
        batch_id=batch.id,
        batch_no=payload.batch_no,
        quantity=payload.quantity,
        purchase_price=payload.purchase_price,
        received_by=payload.received_by,
        received_at=datetime.now(),
        status="completed",
        remark=payload.remark,
    )
    db.add(inbound)
    db.commit()
    db.refresh(inbound)
    return inbound


def list_batches(db: Session):
    return db.query(MedicineBatch).order_by(MedicineBatch.expiry_date.asc(), MedicineBatch.id.desc()).all()


def issue_prescription(db: Session, payload: PrescriptionIssueCreate, issued_by: int) -> PrescriptionIssue:
    medicine = db.get(Medicine, payload.medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    if medicine.current_stock < payload.quantity:
        raise BusinessError(400, "药品库存不足")
    batches = (
        db.query(MedicineBatch)
        .filter(MedicineBatch.medicine_id == medicine.id, MedicineBatch.remaining_quantity > 0)
        .order_by(MedicineBatch.expiry_date.asc(), MedicineBatch.id.asc())
        .all()
    )
    remain = payload.quantity
    allocation: list[tuple[MedicineBatch, int]] = []
    for batch in batches:
        if remain <= 0:
            break
        take = min(remain, batch.remaining_quantity)
        allocation.append((batch, take))
        remain -= take
    if remain > 0:
        raise BusinessError(400, "可用批次库存不足")
    issue_no = f"{generate_no('PR')}{str(int(datetime.now().timestamp()))[-4:]}"
    issue = PrescriptionIssue(
        issue_no=issue_no,
        patient_name=payload.patient_name,
        doctor_name=payload.doctor_name,
        issued_by=issued_by,
        issued_at=datetime.now(),
        total_amount=Decimal(str(payload.unit_price or medicine.selling_price)) * payload.quantity,
        status="completed",
        remark=payload.remark,
    )
    db.add(issue)
    db.flush()
    for batch, qty in allocation:
        batch.remaining_quantity -= qty
        item = PrescriptionIssueItem(
            issue_id=issue.id,
            medicine_id=medicine.id,
            batch_id=batch.id,
            quantity=qty,
            unit_price=payload.unit_price or medicine.selling_price,
        )
        db.add(item)
    medicine.current_stock -= payload.quantity
    db.commit()
    db.refresh(issue)
    return issue


def create_stock_count(db: Session, payload: StockCountCreate) -> StockCount:
    medicine = db.get(Medicine, payload.medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    difference = payload.counted_quantity - medicine.current_stock
    count_no = f"{generate_no('SC')}{str(int(datetime.now().timestamp()))[-4:]}"
    count = StockCount(
        count_no=count_no,
        medicine_id=medicine.id,
        system_quantity=medicine.current_stock,
        counted_quantity=payload.counted_quantity,
        difference_qty=difference,
        counted_by=payload.counted_by,
        counted_at=datetime.now(),
        status="submitted",
        remark=payload.remark,
    )
    db.add(count)
    db.flush()
    adjustment = AdjustmentOrder(
        order_no=f"{generate_no('ADJ')}{str(int(datetime.now().timestamp()))[-4:]}",
        count_id=count.id,
        medicine_id=medicine.id,
        system_quantity=medicine.current_stock,
        counted_quantity=payload.counted_quantity,
        difference_qty=difference,
        reason="盘点差异",
        status="pending",
        created_by=1,
        remark="系统自动生成盘点调整单",
    )
    db.add(adjustment)
    db.commit()
    db.refresh(count)
    return count


def approve_adjustment(db: Session, adjustment: AdjustmentOrder, approved_by: int) -> AdjustmentOrder:
    if adjustment.status != "pending":
        raise BusinessError(400, "该调整单已处理")
    medicine = db.get(Medicine, adjustment.medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    new_stock = medicine.current_stock + adjustment.difference_qty
    if new_stock < 0:
        raise BusinessError(400, "调整后库存不能小于零")
    medicine.current_stock = new_stock
    adjustment.status = "approved"
    adjustment.approved_by = approved_by
    adjustment.approved_at = datetime.now()
    db.commit()
    db.refresh(adjustment)
    return adjustment


def create_purchase_order(db: Session, payload: PurchaseOrderCreate):
    from app.models import PurchaseOrder

    medicine = db.get(Medicine, payload.medicine_id)
    supplier = db.get(Supplier, payload.supplier_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    if not supplier:
        raise BusinessError(404, "未找到供应商信息")
    order = PurchaseOrder(
        order_no=f"{generate_no('PO')}{str(int(datetime.now().timestamp()))[-4:]}",
        medicine_id=medicine.id,
        supplier_id=supplier.id,
        requested_qty=payload.requested_qty,
        suggested_qty=payload.suggested_qty,
        reason=payload.reason,
        status="pending",
        created_by=payload.created_by,
        remark=payload.remark,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
