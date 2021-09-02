#MONGODB_CLIENT_URL = 'mongodb://127.0.0.1:27017'
import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Import secrets
SECRET_DIR = os.path.join(BASE_DIR, '.secrets')
DB_SETTING_SECRETS = json.load(open(os.path.join(SECRET_DIR, 'db_connection_secrets.json'), 'rb'))

# Set URI
MONGODB_CLIENT_URL = f'mongodb+srv://{DB_SETTING_SECRETS["USER_ID"]}:{DB_SETTING_SECRETS["PASSWORD"]}@' \
                     f'{DB_SETTING_SECRETS["DB_URL"]}/{DB_SETTING_SECRETS["DB_NAME"]}?retryWrites=true&w=majority'
