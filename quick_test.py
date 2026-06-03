"""Quick test to check server startup"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Try importing main
from main import app
print("App imported OK")

# Check templates
import os.path
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend", "templates")
print(f"Templates dir: {templates_dir}")
print(f"Exists: {os.path.isdir(templates_dir)}")
print(f"Files: {os.listdir(templates_dir)}")

# Test running the app
import uvicorn
print("Starting uvicorn...")
uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
