from auth.database import engine, SessionLocal
from auth.models import User
from auth.database import Base

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    users = [
        User(username="finance_user", password="test", role="finance"),
        User(username="hr_user", password="test", role="hr"),
        User(username="employee_user", password="test", role="employees"),
        User(username="admin", password="admin", role="c_level"),
    ]

    for user in users:
        if not db.query(User).filter(User.username == user.username).first():
            db.add(user)

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    print("✅ Database initialized")
