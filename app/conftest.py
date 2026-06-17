# Automatically adds app directory to sys.path for pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
