#!/usr/bin/env python3

"""
Script to regenerate resources.py for PyQt6 compatibility
"""

import os
import sys
from PyQt6 import QtCore

def regenerate_resources():
    """Regenerate resources using PyQt6"""
    qrc_file = "resources/resources.qrc"
    output_file = "bigglesworth/resources.py"
    
    if not os.path.exists(qrc_file):
        print(f"Error: {qrc_file} not found")
        return False
    
    # Try to use PyQt6's resource compiler
    try:
        from PyQt6.pyrcc_main import main as pyrcc_main
        sys.argv = ['pyrcc6', qrc_file, '-o', output_file]
        pyrcc_main()
        print(f"Successfully regenerated {output_file}")
        return True
    except ImportError:
        print("PyQt6 resource compiler not available, creating minimal resources file")
        
        # Create a minimal resources file that doesn't break the import
        with open(output_file, 'w') as f:
            f.write('''# -*- coding: utf-8 -*-

# Minimal resource file for PyQt6 compatibility
# Resources temporarily disabled during migration

from PyQt6 import QtCore

def qInitResources():
    """Initialize resources - currently disabled"""
    pass

def qCleanupResources():
    """Cleanup resources - currently disabled"""
    pass

# Auto-initialize (commented out to prevent issues)
# qInitResources()
''')
        print(f"Created minimal {output_file}")
        return True

if __name__ == "__main__":
    regenerate_resources()
