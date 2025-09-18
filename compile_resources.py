#!/usr/bin/env python3

"""
Python-based Qt resource compiler for PyQt6
This script reads the .qrc file and generates a resources.py file compatible with PyQt6
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
    """Compile Qt resources for PyQt6"""
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

qt_resource_data = {
'''
    
    # Dictionary to store resource data
    resource_data = {}
    resource_names = {}
    
    # Process each qresource element
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
                resource_name = prefix + alias
                if resource_name.startswith('/'):
                    resource_name = resource_name[1:]
                
                # Store the data
                resource_data[resource_name] = file_data
                resource_names[resource_name] = len(resource_data) - 1
    
    # Add resource data to the file
    for i, (name, data) in enumerate(resource_data.items()):
        encoded_data = base64.b64encode(data).decode('ascii')
        resources_content += f'    {i}: {repr(encoded_data)},\n'
    
    resources_content += '}\n\n'
    
    # Add resource names mapping
    resources_content += 'qt_resource_name = {\n'
    for name, index in resource_names.items():
        resources_content += f'    {repr(name)}: {index},\n'
    resources_content += '}\n\n'
    
    # Add resource structure
    resources_content += '''qt_resource_struct = {}

def qInitResources():
    """Initialize Qt resources"""
    QtCore.qRegisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    """Cleanup Qt resources"""
    QtCore.qUnregisterResourceData(0x03, qt_resource_struct, qt_resource_name, qt_resource_data)

# Auto-initialize resources
qInitResources()
'''
    
    # Write the resources.py file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(resources_content)
        print(f"Successfully compiled {len(resource_data)} resources to {output_file}")
        return True
    except IOError as e:
        print(f"Error writing {output_file}: {e}")
        return False

if __name__ == "__main__":
    success = compile_resources()
    sys.exit(0 if success else 1)
