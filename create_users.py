# create_users.py

import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tttracker.settings')
django.setup()

from django.contrib.auth.models import User

def create_user(username, password, email=None):
    try:
        if User.objects.filter(username=username).exists():
            print(f"User '{username}' already exists.")
            return

        user = User.objects.create_user(username=username, email=email, password=password)
        print(f"User '{username}' created successfully.")
        return user
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python create_users.py <username> <password> [email]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) == 4 else None

    create_user(username, password, email)