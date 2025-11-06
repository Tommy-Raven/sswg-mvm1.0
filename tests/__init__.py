# __init__.py
"""
Grimoire v4.8 — Test Suite Initialization
Ensures pytest recognizes the test package and paths correctly.
"""

import os
import sys

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

