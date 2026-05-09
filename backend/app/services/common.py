from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import ExpiryWarning, Medicine, MedicineBatch, User


def generate_no(prefix: str, current_date: date | None = None) -> str:
    current_date = current_date or date.today()
    return f"{prefix}-{current_date.strftime('%Y%m%d')}"


def refresh_expiry_warnings(db: Session, warning_days: int) -> None:
    db.query(ExpiryWarning).delete()
    batches = db.scalars(select(MedicineBatch).where(MedicineBatch.remaining_quantity > 0)).all()
    for batch in batches:
        medicine = db.get(Medicine, batch.medicine_id)
        if not medicine:
            continue
        days_left = (batch.expiry_date - date.today()).days
        if days_left <= warning_days:
            if days_left <= 0:
                level = "critical"
            elif days_left <= 30:
                level = "high"
            elif days_left <= 60:
                level = "medium"
            else:
                level = "info"
            db.add(
                ExpiryWarning(
                    medicine_id=medicine.id,
                    batch_id=batch.id,
                    warning_type="近效期预警",
                    days_left=days_left,
                    warning_level=level,
                    status="active",
                )
            )
    db.commit()


def ensure_admin_account(db: Session, password_hash: str) -> None:
    admin = db.query(User).filter(User.username == "admin").one_or_none()
    if admin is None:
        db.add(
            User(
                username="admin",
                password_hash=password_hash,
                nickname="系统管理员",
                role="admin",
                phone="13800000000",
                email="admin@clinic.local",
                status="enabled",
            )
        )
        db.commit()
        return
    changed = False
    try:
        password_ok = verify_password("123456", admin.password_hash)
    except Exception:
        password_ok = False
    if not password_ok:
        admin.password_hash = password_hash
        changed = True
    if admin.role != "admin":
        admin.role = "admin"
        changed = True
    if admin.status != "enabled":
        admin.status = "enabled"
        changed = True
    if changed:
        db.commit()


def ensure_demo_accounts(db: Session, password_hash: str) -> None:
    accounts = [
        {
            "username": "admin",
            "nickname": "系统管理员",
            "role": "admin",
            "phone": "13800000000",
            "email": "admin@clinic.local",
        },
        {
            "username": "pharmacy",
            "nickname": "药房管理员",
            "role": "pharmacist",
            "phone": "13800000001",
            "email": "pharmacy@clinic.local",
        },
        {
            "username": "doctor",
            "nickname": "门诊医生",
            "role": "doctor",
            "phone": "13800000002",
            "email": "doctor@clinic.local",
        },
        {
            "username": "buyer",
            "nickname": "采购员",
            "role": "purchaser",
            "phone": "13800000003",
            "email": "buyer@clinic.local",
        },
    ]
    for account in accounts:
        user = db.query(User).filter(User.username == account["username"]).one_or_none()
        if user is None:
            db.add(User(password_hash=password_hash, status="enabled", **account))
            continue
        try:
            password_ok = verify_password("123456", user.password_hash)
        except Exception:
            password_ok = False
        if not password_ok:
            user.password_hash = password_hash
        user.nickname = account["nickname"]
        user.role = account["role"]
        user.phone = account["phone"]
        user.email = account["email"]
        user.status = "enabled"
    db.commit()
