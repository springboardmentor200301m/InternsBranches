from auth.database import engine, SessionLocal
from auth.models import User
from auth.database import Base

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    users = [
        User(username="finance_user", password="fin123", role="finance"),
        User(username="marketing_user", password="mark123", role="marketing"),
        User(username="hr_user", password="hr123", role="hr"),
        User(username="engineering_user", password="eng123", role="engineering"),
        User(username="employee_user", password="emp123", role="employees"),
        User(username="admin", password="admin123", role="c_level"),
    ]

    for user in users:
        if not db.query(User).filter(User.username == user.username).first():
            db.add(user)

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized with all RBAC roles")
