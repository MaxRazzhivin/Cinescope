import os
from dotenv import load_dotenv

load_dotenv()

class SuperAdminCreds:
    SUPER_ADMIN_USERNAME = os.getenv('SUPER_ADMIN_USERNAME')
    SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD')