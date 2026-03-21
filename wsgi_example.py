"""
WSGI configuration for PythonAnywhere deployment.

Instructions:
1. Copy this file content to your PythonAnywhere WSGI configuration file
2. Replace '7miwork' with your actual PythonAnywhere username
3. Save and reload your web app
"""

import sys

# Add project path to sys.path
# IMPORTANT: Replace '7miwork' with your PythonAnywhere username
path = '/home/7miwork/Trade-copy'
if path not in sys.path:
    sys.path.append(path)

# Import Flask app as 'application' (required by WSGI)
from app import app as application