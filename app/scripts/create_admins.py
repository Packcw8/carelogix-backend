import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# scripts/create_admins.py
import uuid
from app.models import User, Agency
from app.database import SessionLocal
from app.auth.auth_utils import hash_password  # ✅ Correct import

# 🔧 Define the admins you want to create here
admins_to_create = [
    {
        "email": "admin1@example.com",
        "password": "AdminPassword1!",
        "full_name": "Alice Admin",
        "agency_name": "Bright Futures"
    },
    {
        "email": "admin2@example.com",
        "password": "AdminPassword2!",
        "full_name": "Bob Supervisor",
        "agency_name": "New Pathways"
    },
]

db = SessionLocal()

for admin in admins_to_create:
    # Check for agency
    agency = db.query(Agency).filter(Agency.name == admin["agency_name"]).first()
    if not agency:
        print(f"❌ Skipped {admin['email']} — agency '{admin['agency_name']}' not found.")
        continue

    # Check if user exists
    existing = db.query(User).filter(User.email == admin["email"]).first()
    if existing:
        print(f"⚠️ User already exists: {admin['email']}")
        continue

    # ✅ Use hash_password from your auth_utils
    new_admin = User(
        id=str(uuid.uuid4()),
        email=admin["email"],
        password_hash=hash_password(admin["password"]),
        full_name=admin["full_name"],
        is_admin=True,
        agency_id=agency.id
    )
    db.add(new_admin)
    print(f"✅ Created admin: {admin['email']}")

db.commit()
db.close()
print("🏁 Admin creation complete.")

