# build.py
import PyInstaller.__main__
import os
import subprocess
import shutil
from pathlib import Path

def build():
    # Get absolute paths
    current_dir = Path.cwd()
    build_dir = current_dir / 'build'
    dist_dir = current_dir / 'dist'
    installer_dir = current_dir / 'installer'
    
    # Clean previous builds
    for dir in [build_dir, dist_dir, installer_dir]:
        if dir.exists():
            shutil.rmtree(dir)
    
    # Create exe
    PyInstaller.__main__.run([
        'main.py',
        '--onefile',
        '--noconsole',
        '--add-data', '../db.sqlite;.',
        '--add-data', 'styles.qss;.',
        '--icon', 'app_icon.ico',
        '--name', 'CurlyOctoEngine'
    ])

    # Create installer directory
    installer_dir.mkdir(exist_ok=True)

    # Run Inno Setup Compiler
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if os.path.exists(inno_compiler):
        # Use absolute paths
        script_path = current_dir / 'installer_script.iss'
        process = subprocess.run(
            [inno_compiler, str(script_path)], 
            capture_output=True, 
            text=True
        )
        
        # Print the actual output from Inno Setup
        if process.stdout:
            print("Inno Setup output:")
            print(process.stdout)
        if process.stderr:
            print("Inno Setup errors:")
            print(process.stderr)
            
        if process.returncode == 0:
            print("Installer created successfully!")
        else:
            print("Error creating installer")
    else:
        print("Inno Setup not found. Please install it first.")

if __name__ == "__main__":
    build()