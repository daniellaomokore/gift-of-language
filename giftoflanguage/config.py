import os
from dotenv import load_dotenv

# load environmental variables
load_dotenv()

# Mysqlworkbench
# environmental variables stored

DATABASENAME = "boredapp_users"
USER = os.environ.get('USER')
DATABASEPASSWORD = os.environ.get('DATABASEPASSWORD')  # THIS IS YOUR MYSQLWORKBENCH PASSWORD
HOST = os.environ.get('HOST')

# secret key
SECRET_KEY = os.environ.get('SECRET_KEY')

