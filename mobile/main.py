import sys
import os

# Ensure mobile app directory is in Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import GuidePotagerApp

if __name__ == '__main__':
    GuidePotagerApp().run()
