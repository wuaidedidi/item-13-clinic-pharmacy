from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AdjustmentOrder, InboundOrder, Medicine, MedicineBatch, PrescriptionIssue, PurchaseOrder, StockCount, Supplier


def build_dashboard_summary(db: Session, warning_days: int):
    today = date.today()
    cutoff = today + timedelta(days=warning_days)

    expiring_batches = (
        db.query(MedicineBatch, Medicine)
        .join(Medicine, Medicine.id == MedicineBatch.medicine_id)
        .filter(MedicineBatch.remaining_quantity > 0)
        .filter(MedicineBatch.expiry_date <= cutoff)
        .order_by(MedicineBatch.expiry_date.asc())
        .all()
    )
    expiring_batch_count = len(expiring_batches)
    shortage_medicines = db.query(Medicine).filter(Medicine.current_stock <= Medicine.safety_stock).all()
    pending_purchase_count = db.query(PurchaseOrder).filter(PurchaseOrder.status == "pending").count()
    today_issue_amount = (
        db.query(func.coalesce(func.sum(PrescriptionIssue.total_amount), 0))
        .filter(func.date(PrescriptionIssue.issued_at) == today)
        .scalar()
    )
    turnover_rate = 0.0
    total_stock = db.query(func.coalesce(func.sum(Medicine.current_stock), 0)).scalar() or 0
    total_inbound = db.query(func.coalesce(func.sum(InboundOrder.quantity), 0)).scalar() or 0
    if total_stock:
        turnover_rate = round(float(total_inbound) / float(total_stock), 2)

    return {
        "expiring_batch_count": expiring_batch_count,
        "turnover_rate": turnover_rate,
        "today_issue_amount": Decimal(str(today_issue_amount or 0)),
        "shortage_medicine_count": len(shortage_medicines),
        "pending_purchase_count": pending_purchase_count,
        "expiring_batches": [
            {
                "medicineName": medicine.name,
                "batchNo": batch.batch_no,
                "daysLeft": (batch.expiry_date - today).days,
                "remainingQuantity": batch.remaining_quantity,
                "location": batch.location or medicine.location or "-",
            }
            for batch, medicine in expiring_batches[:6]
        ],
        "shortage_items": [
            {
                "medicineName": medicine.name,
                "currentStock": medicine.current_stock,
                "safetyStock": medicine.safety_stock,
                "location": medicine.location or "-",
            }
            for medicine in shortage_medicines[:6]
        ],
        "pending_adjustments": [
            {
                "orderNo": item.order_no,
                "medicineName": db.get(Medicine, item.medicine_id).name if db.get(Medicine, item.medicine_id) else "-",
                "differenceQty": item.difference_qty,
                "reason": item.reason,
            }
            for item in db.query(AdjustmentOrder).filter(AdjustmentOrder.status == "pending").order_by(AdjustmentOrder.updated_at.desc()).limit(6)
        ],
        "recent_inbounds": [
            {
                "orderNo": item.order_no,
                "medicineName": db.get(Medicine, item.medicine_id).name if db.get(Medicine, item.medicine_id) else "-",
                "quantity": item.quantity,
                "receivedBy": item.received_by,
                "receivedAt": item.received_at,
            }
            for item in db.query(InboundOrder).order_by(InboundOrder.received_at.desc()).limit(6)
        ],
        "recent_issues": [
            {
                "issueNo": item.issue_no,
                "patientName": item.patient_name,
                "doctorName": item.doctor_name,
                "totalAmount": item.total_amount,
                "issuedAt": item.issued_at,
            }
            for item in db.query(PrescriptionIssue).order_by(PrescriptionIssue.issued_at.desc()).limit(6)
        ],
        "role_tiles": [
            {"role": "admin", "title": "系统管理员", "count": db.query(func.count()).select_from(Medicine).scalar() or 0},
            {"role": "pharmacist", "title": "药房管理员", "count": db.query(func.count()).select_from(StockCount).scalar() or 0},
            {"role": "doctor", "title": "医生", "count": db.query(func.count()).select_from(PrescriptionIssue).scalar() or 0},
            {"role": "purchaser", "title": "采购员", "count": pending_purchase_count},
        ],
    }
