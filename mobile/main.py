import sys
import os

# Ensure mobile app directory is in Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import GuidePotagerTropicalApp

if __name__ == '__main__':
    GuidePotagerTropicalApp().run()
