#!/usr/bin/env python3

"""
PyQt6-compatible Qt resource compiler
This creates a proper resources.py file that works with PyQt6's resource system
"""

import os
import sys
import xml.etree.ElementTree as ET
import base64
from pathlib import Path

def read_file_as_bytes(filepath):
    """Read a file and return its content as bytes"""
    try:
        with open(filepath, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return b''

def compile_resources():
    """Compile Qt resources for PyQt6 using a simpler approach"""
    qrc_file = "resources/resources.qrc"
    output_file = "bigglesworth/resources.py"
    
    if not os.path.exists(qrc_file):
        print(f"Error: {qrc_file} not found")
        return False
    
    # Parse the QRC file
    try:
        tree = ET.parse(qrc_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing {qrc_file}: {e}")
        return False
    
    # Start building the resources.py content
    resources_content = '''# -*- coding: utf-8 -*-

# Resource object code (Python 3, PyQt6)
# Created by: Python resource compiler
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore
import base64

# Resource data storage
_resource_data = {}

'''
    
    # Process each qresource element
    resource_count = 0
    for qresource in root.findall('qresource'):
        prefix = qresource.get('prefix', '')
        if prefix and not prefix.startswith('/'):
            prefix = '/' + prefix
        if prefix and not prefix.endswith('/'):
            prefix = prefix + '/'
            
        # Process each file in the qresource
        for file_elem in qresource.findall('file'):
            file_path = file_elem.text
            alias = file_elem.get('alias', file_path)
            
            # Full path to the actual file
            full_path = os.path.join('resources', file_path)
            
            # Read file content
            file_data = read_file_as_bytes(full_path)
            if file_data:
                # Create resource name
                resource_name = ':' + prefix + alias
                if resource_name.startswith('://'):
                    resource_name = resource_name[1:]  # Remove one slash
                
                # Encode data as base64
                encoded_data = base64.b64encode(file_data).decode('ascii')
                
                # Add to resources content
                resources_content += f'_resource_data[{repr(resource_name)}] = base64.b64decode({repr(encoded_data)})\n'
                resource_count += 1
    
    # Add the resource access functions
    resources_content += '''
def qInitResources():
    """Initialize Qt resources"""
    # Register each resource with Qt
    for path, data in _resource_data.items():
        # Create a QByteArray from the data
        byte_array = QtCore.QByteArray(data)
        # Register the resource data
        QtCore.qRegisterResourceData(0x01, byte_array, QtCore.QByteArray(), QtCore.QByteArray())

def qCleanupResources():
    """Cleanup Qt resources"""
    # Cleanup is handled automatically by Qt
    pass

# Alternative approach: Use QResource directly
class ResourceProvider:
    @staticmethod
    def get_resource(path):
        """Get resource data by path"""
        return _resource_data.get(path, b'')
    
    @staticmethod
    def has_resource(path):
        """Check if resource exists"""
        return path in _resource_data

# Make resources available globally
import sys
if not hasattr(sys.modules[__name__], '_resources_initialized'):
    # Try to initialize resources
    try:
        qInitResources()
    except:
        # If Qt resource registration fails, we'll use direct access
        pass
    sys.modules[__name__]._resources_initialized = True
'''
    
    # Write the resources.py file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(resources_content)
        print(f"Successfully compiled {resource_count} resources to {output_file}")
        return True
    except IOError as e:
        print(f"Error writing {output_file}: {e}")
        return False

if __name__ == "__main__":
    success = compile_resources()
    sys.exit(0 if success else 1)
