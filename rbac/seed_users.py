"""
Seed the database with sample user accounts for testing
"""

from sqlalchemy.orm import Session
from database import SessionLocal, User, init_database
from auth import hash_password

SAMPLE_USERS = [
    {
        "username": "clevel_admin",
        "email": "clevel@company.com",
        "password": "clevel123",
        "role": "C-Level"
    },
    {
        "username": "finance_user",
        "email": "finance@company.com",
        "password": "finance123",
        "role": "Finance"
    },
    {
        "username": "marketing_user",
        "email": "marketing@company.com",
        "password": "marketing123",
        "role": "Marketing"
    },
    {
        "username": "hr_user",
        "email": "hr@company.com",
        "password": "hr123",
        "role": "HR"
    },
    {
        "username": "engineering_user",
        "email": "engineering@company.com",
        "password": "engineering123",
        "role": "Engineering"
    },
    {
        "username": "employee_user",
        "email": "employee@company.com",
        "password": "employee123",
        "role": "Employees"
    }
]


def create_users(db: Session):
    """Create sample users in the database"""
    
    print("\n" + "="*60)
    print("CREATING SAMPLE USER ACCOUNTS")
    print("="*60 + "\n")
    
    created_count = 0
    
    for user_data in SAMPLE_USERS:
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.username == user_data["username"]
        ).first()
        
        if existing_user:
            print(f"⚠️  User '{user_data['username']}' already exists, skipping...")
            continue
        
        # Create new user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            role=user_data["role"]
        )
        
        db.add(user)
        created_count += 1
        print(f"✅ Created user: {user_data['username']} (Role: {user_data['role']})")
    
    db.commit()
    
    print(f"\n✅ Successfully created {created_count} new users")
    
    # Display login credentials
    print("\n" + "="*60)
    print("LOGIN CREDENTIALS FOR TESTING")
    print("="*60 + "\n")
    
    for user_data in SAMPLE_USERS:
        print(f"Role: {user_data['role']}")
        print(f"  Username: {user_data['username']}")
        print(f"  Password: {user_data['password']}")
        print()


def main():
    """Main function to initialize database and create users"""
    
    # Initialize database
    print("Initializing database...")
    init_database()
    
    # Create users
    db = SessionLocal()
    try:
        create_users(db)
    finally:
        db.close()
    
    print("="*60)
    print("✅ DATABASE SETUP COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()