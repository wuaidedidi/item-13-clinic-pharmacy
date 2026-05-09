from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import BusinessError
from app.core.response import success
from app.dependencies import get_current_user, require_roles
from app.models import AdjustmentOrder, InboundOrder, Medicine, MedicineBatch, PrescriptionIssue, PurchaseOrder, StockCount, Supplier, User
from app.schemas import (
    InboundCreate,
    MedicineCreate,
    MedicineUpdate,
    PurchaseOrderCreate,
    StockCountCreate,
    SupplierCreate,
    SupplierUpdate,
    PrescriptionIssueCreate,
)
from app.services.common import refresh_expiry_warnings
from app.services.dashboard import build_dashboard_summary
from app.services import inventory

router = APIRouter(prefix="/api", tags=["业务接口"])
settings = get_settings()


def medicine_name(db: Session, medicine_id: int) -> str:
    medicine = db.get(Medicine, medicine_id)
    return medicine.name if medicine else "-"


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(build_dashboard_summary(db, settings.expiry_warning_days))


@router.get("/medicines")
def list_medicines(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = inventory.list_medicines(db)
    return success([
        {
            **{
                "id": item.id,
                "code": item.code,
                "name": item.name,
                "specification": item.specification,
                "unit": item.unit,
                "category": item.category,
                "currentStock": item.current_stock,
                "safetyStock": item.safety_stock,
                "sellingPrice": item.selling_price,
                "purchasePrice": item.purchase_price,
                "expiryWarningDays": item.expiry_warning_days,
                "supplierId": item.supplier_id,
                "supplierName": item.supplier.name if item.supplier else "-",
                "location": item.location,
                "status": item.status,
                "createdAt": item.created_at,
            }
        }
        for item in rows
    ])


@router.post("/medicines")
def create_medicine(
    payload: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "pharmacist")),
):
    return success(inventory.create_medicine(db, payload), "药品已新增")


@router.put("/medicines/{medicine_id}")
def update_medicine(
    medicine_id: int,
    payload: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "pharmacist")),
):
    medicine = db.get(Medicine, medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    return success(inventory.update_medicine(db, medicine, payload), "药品已更新")


@router.delete("/medicines/{medicine_id}")
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    medicine = db.get(Medicine, medicine_id)
    if not medicine:
        raise BusinessError(404, "未找到药品信息")
    inventory.delete_medicine(db, medicine)
    return success(None, "药品已删除")


@router.get("/suppliers")
def list_suppliers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return success(db.query(Supplier).order_by(Supplier.updated_at.desc()).all())


@router.post("/suppliers")
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "purchaser", "pharmacist")),
):
    if db.query(Supplier).filter(Supplier.name == payload.name).one_or_none():
        raise BusinessError(409, "供应商名称已存在")
    supplier = Supplier(**payload.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return success(supplier, "供应商已新增")


@router.put("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "purchaser", "pharmacist")),
):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise BusinessError(404, "未找到供应商信息")
    for key, value in payload.model_dump().items():
        setattr(supplier, key, value)
    db.commit()
    db.refresh(supplier)
    return success(supplier, "供应商已更新")


@router.delete("/suppliers/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    supplier = db.get(Supplier, supplier_id)
    if not supplier:
        raise BusinessError(404, "未找到供应商信息")
    has_medicine = db.query(Medicine.id).filter(Medicine.supplier_id == supplier.id).first()
    has_purchase = db.query(PurchaseOrder.id).filter(PurchaseOrder.supplier_id == supplier.id).first()
    if has_medicine:
        raise BusinessError(400, "该供应商已有药品目录关联，无法删除")
    if has_purchase:
        raise BusinessError(400, "该供应商已有采购记录，无法删除")
    db.delete(supplier)
    db.commit()
    return success(None, "供应商已删除")


@router.get("/batches")
def list_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = inventory.list_batches(db)
    return success([
        {
            "id": item.id,
            "medicineId": item.medicine_id,
            "medicineName": medicine_name(db, item.medicine_id),
            "supplierId": item.supplier_id,
            "batchNo": item.batch_no,
            "inboundOrderNo": item.inbound_order_no,
            "quantity": item.quantity,
            "remainingQuantity": item.remaining_quantity,
            "productionDate": item.production_date,
            "expiryDate": item.expiry_date,
            "inboundDate": item.inbound_date,
            "location": item.location,
            "status": item.status,
            "remark": item.remark,
        }
        for item in rows
    ])


@router.post("/inbounds")
def create_inbound(
    payload: InboundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "pharmacist", "purchaser")),
):
    inbound = inventory.create_inbound(db, payload)
    refresh_expiry_warnings(db, settings.expiry_warning_days)
    return success(inbound, "批次入库完成")


@router.get("/inbounds")
def list_inbounds(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(InboundOrder).order_by(InboundOrder.received_at.desc()).all()
    return success([
        {
            "id": item.id,
            "orderNo": item.order_no,
            "medicineId": item.medicine_id,
            "medicineName": medicine_name(db, item.medicine_id),
            "supplierId": item.supplier_id,
            "batchNo": item.batch_no,
            "quantity": item.quantity,
            "purchasePrice": item.purchase_price,
            "receivedBy": item.received_by,
            "receivedAt": item.received_at,
            "status": item.status,
            "remark": item.remark,
        }
        for item in rows
    ])


@router.post("/prescriptions")
def issue_prescription(
    payload: PrescriptionIssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "doctor", "pharmacist")),
):
    issue = inventory.issue_prescription(db, payload, current_user.id)
    refresh_expiry_warnings(db, settings.expiry_warning_days)
    return success(issue, "处方领用完成")


@router.get("/prescriptions")
def list_prescriptions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(PrescriptionIssue).order_by(PrescriptionIssue.issued_at.desc()).all()
    return success(rows)


@router.get("/warnings")
def list_warnings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    refresh_expiry_warnings(db, settings.expiry_warning_days)
    rows = db.query(MedicineBatch, Medicine).join(Medicine, Medicine.id == MedicineBatch.medicine_id).filter(MedicineBatch.remaining_quantity > 0).order_by(MedicineBatch.expiry_date.asc()).all()
    return success([
        {
            "batchId": batch.id,
            "medicineId": medicine.id,
            "medicineName": medicine.name,
            "specification": medicine.specification,
            "batchNo": batch.batch_no,
            "remainingQuantity": batch.remaining_quantity,
            "expiryDate": batch.expiry_date,
            "daysLeft": (batch.expiry_date - datetime.today().date()).days,
            "location": batch.location or medicine.location,
            "level": "critical" if (batch.expiry_date - datetime.today().date()).days <= 0 else "high" if (batch.expiry_date - datetime.today().date()).days <= 30 else "medium" if (batch.expiry_date - datetime.today().date()).days <= 60 else "info",
        }
        for batch, medicine in rows
        if (batch.expiry_date - datetime.today().date()).days <= settings.expiry_warning_days
    ])


@router.post("/stock-counts")
def create_stock_count(
    payload: StockCountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "pharmacist")),
):
    return success(inventory.create_stock_count(db, payload), "盘点单已提交，调整单已生成")


@router.get("/stock-counts")
def list_stock_counts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(StockCount).order_by(StockCount.counted_at.desc()).all()
    return success([
        {
            "id": item.id,
            "countNo": item.count_no,
            "medicineId": item.medicine_id,
            "medicineName": medicine_name(db, item.medicine_id),
            "systemQuantity": item.system_quantity,
            "countedQuantity": item.counted_quantity,
            "differenceQty": item.difference_qty,
            "countedBy": item.counted_by,
            "countedAt": item.counted_at,
            "status": item.status,
            "remark": item.remark,
        }
        for item in rows
    ])


@router.get("/adjustments")
def list_adjustments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(AdjustmentOrder).order_by(AdjustmentOrder.updated_at.desc()).all()
    return success([
        {
            "id": item.id,
            "orderNo": item.order_no,
            "medicineId": item.medicine_id,
            "medicineName": medicine_name(db, item.medicine_id),
            "systemQuantity": item.system_quantity,
            "countedQuantity": item.counted_quantity,
            "differenceQty": item.difference_qty,
            "reason": item.reason,
            "status": item.status,
            "approvedAt": item.approved_at,
            "remark": item.remark,
        }
        for item in rows
    ])


@router.put("/adjustments/{adjustment_id}/approve")
def approve_adjustment(
    adjustment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    adjustment = db.get(AdjustmentOrder, adjustment_id)
    if not adjustment:
        raise BusinessError(404, "未找到调整单")
    return success(inventory.approve_adjustment(db, adjustment, current_user.id), "调整单已确认")


@router.post("/purchases")
def create_purchase(
    payload: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "purchaser", "pharmacist")),
):
    return success(inventory.create_purchase_order(db, payload), "采购申请已提交")


@router.get("/purchases")
def list_purchases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(PurchaseOrder).order_by(PurchaseOrder.updated_at.desc()).all()
    return success([
        {
            "id": item.id,
            "orderNo": item.order_no,
            "medicineId": item.medicine_id,
            "medicineName": medicine_name(db, item.medicine_id),
            "supplierId": item.supplier_id,
            "supplierName": db.get(Supplier, item.supplier_id).name if db.get(Supplier, item.supplier_id) else "-",
            "requestedQty": item.requested_qty,
            "suggestedQty": item.suggested_qty,
            "reason": item.reason,
            "status": item.status,
            "createdBy": item.created_by,
            "reviewedAt": item.reviewed_at,
            "remark": item.remark,
        }
        for item in rows
    ])


@router.put("/purchases/{purchase_id}/approve")
def approve_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "pharmacist")),
):
    item = db.get(PurchaseOrder, purchase_id)
    if not item:
        raise BusinessError(404, "未找到采购单")
    if item.status != "pending":
        raise BusinessError(400, "该采购单已处理")
    item.status = "approved"
    item.reviewed_by = current_user.id
    item.reviewed_at = datetime.now()
    db.commit()
    db.refresh(item)
    return success(item, "采购单已通过")
