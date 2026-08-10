name: Build Executable

on: [push, workflow_dispatch]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies & PyInstaller
        run: |
          pip install pyinstaller
          # Add any other libraries your app uses here (e.g., pip install requests)
          
      - name: Build EXE
        run: pyinstaller --onefile --noconsole main.py
        
      - name: Upload Executable
        uses: actions/upload-artifact@v4
        with:
          name: MyPythonApp-Windows
          path: dist/main.exe
