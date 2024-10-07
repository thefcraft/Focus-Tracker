@echo off
start cmd /c "python main-alpha-v0.01.py"
cd "macro"
cd "frontend/alpha-v0.01"
start cmd /c "npm run dev"
cd "../../backend/alpha-v0.01"
start cmd /c "python main.py"