#!/usr/bin/env python3
"""
Development runner script for Gold Sentiment Analysis
Starts both backend and frontend in development mode
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def run_backend():
    """Run Flask backend server"""
    print("🚀 Starting Flask backend...")
    backend_path = os.path.join(os.getcwd(), 'backend')
    try:
        subprocess.run([sys.executable, 'app.py'], cwd=backend_path, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    
    """Run React frontend server"""
    print("🚀 Starting React frontend...")
    frontend_path = os.path.join(os.getcwd(), 'frontend')
    try:
        subprocess.run(['npm', 'start'], cwd=frontend_path, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main development runner"""
    print("🏗️  Gold Sentiment Analysis - Development Mode")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Error: Run this script from the project root directory")
        print("   Expected structure: backend/ and frontend/ folders")
        sys.exit(1)
    
    # Check backend dependencies
    if not os.path.exists('backend/requirements.txt'):
        print("❌ Error: backend/requirements.txt not found")
        sys.exit(1)
    
    # Check frontend dependencies
    if not os.path.exists('frontend/package.json'):
        print("❌ Error: frontend/package.json not found")
        sys.exit(1)
    
    print("✅ Project structure validated")
    print("\n📋 Starting services...")
    print("   - Backend: http://localhost:5000")
    print("   - Frontend: http://localhost:3000")
    print("\n💡 Press Ctrl+C to stop all services\n")
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Start frontend (this will block)
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        sys.exit(0)

if __name__ == '__main__':
    main()