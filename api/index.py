import os
import sys

# Ensure root directory is added to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel serverless entrypoint
app = app
