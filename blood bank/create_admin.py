import hashlib
import os
from datetime import datetime

def create_admin_credentials():
    # Admin credentials
    username = "Blood@123"
    password = "Bank@2511"
    
    # Hash the password for security
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Create admin data
    admin_data = {
        "username": username,
        "password": hashed_password,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Create admin directory if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Save admin credentials to a file
    with open("data/admin_credentials.txt", "w") as f:
        f.write(f"Username: {admin_data['username']}\n")
        f.write(f"Password Hash: {admin_data['password']}\n")
        f.write(f"Created At: {admin_data['created_at']}\n")
    
    print("Admin credentials created successfully!")
    print("Username:", username)
    print("Password has been securely stored.")

if __name__ == "__main__":
    create_admin_credentials() 