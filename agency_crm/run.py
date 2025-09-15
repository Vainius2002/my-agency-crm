#!/usr/bin/env python
import os
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv('/home/vainiusl/py_projects/my-agency-crm/.env')

from app import create_app, db
from app.models import User, Company, Brand, ClientContact, MediaGroup

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Company': Company, 'Brand': Brand, 
            'ClientContact': ClientContact, 'MediaGroup': MediaGroup}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)