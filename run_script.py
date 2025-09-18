#!/usr/bin/env python3
"""
Safe Resource Packer - Script Runner

This script provides npm-style script running for development tasks.
Usage: python run_script.py <script_name>
"""

import json
import sys
import subprocess
import os
from pathlib import Path

def load_scripts():
    """Load scripts from scripts.json."""
    try:
        with open("scripts.json", "r") as f:
            data = json.load(f)
            return data.get("scripts", {})
    except FileNotFoundError:
        print("❌ scripts.json not found")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing scripts.json: {e}")
        return {}

def list_scripts(scripts):
    """List all available scripts."""
    print("📋 Available scripts:")
    print()
    
    # Group scripts by category
    categories = {
        "Build": [],
        "Test": [],
        "Development": [],
        "Release": [],
        "Other": []
    }
    
    for name, command in scripts.items():
        if name.startswith("build"):
            categories["Build"].append((name, command))
        elif name.startswith("test"):
            categories["Test"].append((name, command))
        elif name in ["install", "install:deps", "run", "run:cli", "dev", "lint", "format"]:
            categories["Development"].append((name, command))
        elif name.startswith("release"):
            categories["Release"].append((name, command))
        else:
            categories["Other"].append((name, command))
    
    for category, items in categories.items():
        if items:
            print(f"🔧 {category}:")
            for name, command in items:
                print(f"   {name:<20} - {command}")
            print()

def run_script(script_name, scripts):
    """Run a specific script."""
    if script_name not in scripts:
        print(f"❌ Script '{script_name}' not found")
        print()
        list_scripts(scripts)
        return 1
    
    command = scripts[script_name]
    print(f"🚀 Running script: {script_name}")
    print(f"📝 Command: {command}")
    print()
    
    try:
        # Run the command
        result = subprocess.run(command, shell=True, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Script cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return 1

def main():
    """Main entry point."""
    scripts = load_scripts()
    
    if not scripts:
        print("❌ No scripts found")
        return 1
    
    if len(sys.argv) < 2:
        print("🎯 Safe Resource Packer - Script Runner")
        print("Usage: python run_script.py <script_name>")
        print()
        list_scripts(scripts)
        return 0
    
    script_name = sys.argv[1]
    
    if script_name in ["--help", "-h", "help"]:
        print("🎯 Safe Resource Packer - Script Runner")
        print("Usage: python run_script.py <script_name>")
        print()
        list_scripts(scripts)
        return 0
    
    if script_name in ["--list", "-l", "list"]:
        list_scripts(scripts)
        return 0
    
    return run_script(script_name, scripts)

if __name__ == "__main__":
    sys.exit(main())
