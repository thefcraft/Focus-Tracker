from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import csv
from typing import List, Dict
from pathlib import Path
from datetime import datetime

def get_current_date()->str:
    return datetime.now().strftime('%Y-%m-%d')
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Path to icons and CSV data
ASSETS_DIR = Path(r"C:\ThefCraft\thefcraft-python\FocusTrack\data\assets")
ICON_DIR = Path(r"C:\ThefCraft\thefcraft-python\FocusTrack\data\icon")
CSV_DIR = Path(r"C:\ThefCraft\thefcraft-python\FocusTrack\data\local")

# Route to serve icons
@app.get("/icon/{program_name}.png")
async def get_icon(program_name: str):
    icon_path = ICON_DIR / f"{program_name}.png"
    if not icon_path.exists(): return FileResponse(ASSETS_DIR / "img" / f"null.png")
    return FileResponse(icon_path)


# Route to serve all available CSV files
@app.get("/data/available")
async def get_available_files():
    csv_files = [f.name for f in CSV_DIR.glob("*.csv")]
    return {"available_files": csv_files}


# Route to fetch CSV data
@app.get("/data/{date}.csv", response_model=List[Dict[str, str]])
async def get_data(date: str):
    csv_file = CSV_DIR / f"{date}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    data = []
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({
                "program_name": row["program_name"],
                "window_title": row["window_title"],
                "timestamp": row["timestamp"],
                "duration": row["duration"]
            })
    return data[::-1]

@app.get("/data/", response_model=List[Dict[str, str]])
async def get_data():
    csv_file = CSV_DIR / f"{get_current_date()}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")
    
    data = []
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append({
                "program_name": row["program_name"],
                "window_title": row["window_title"],
                "timestamp": row["timestamp"],
                "duration": row["duration"]
            })
    return data[::-1]

# Example route to display summary from CSV data
@app.get("/summary/{date}")
async def get_summary(date: str):
    csv_file = CSV_DIR / f"{date}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")

    summary = {}
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            program = row["program_name"]
            duration = int(row["duration"])
            if program in summary:
                summary[program] += duration
            else:
                summary[program] = duration
    return summary

@app.get("/summary/")
async def get_summary_today():
    csv_file = CSV_DIR / f"{get_current_date()}.csv"
    if not csv_file.exists():
        raise HTTPException(status_code=404, detail="CSV file not found")

    summary = {}
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            program = row["program_name"]
            duration = int(row["duration"])
            if program in summary:
                summary[program] += duration
            else:
                summary[program] = duration
    return summary


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)