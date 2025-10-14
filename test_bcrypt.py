# test_bcrypt.py
from security import get_password_hash, verify_password

password = "TestPassword123!@#"
hashed = get_password_hash(password)
print(f"Hashed: {hashed}")
print(f"Verification: {verify_password(password, hashed)}")