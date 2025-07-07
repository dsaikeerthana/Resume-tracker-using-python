from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json, os
from datetime import datetime

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATA_FILE = "applications.json"

# Create file if not exists
def init_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)

# Load applications
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save applications
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 🏠 Login page
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 📋 Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, username: str):
    data = load_data()
    user_apps = [app for app in data if app["username"] == username]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "applications": user_apps,
        "username": username
    })

# ➕ Add application
@app.post("/add")
def add_application(
    company: str = Form(...),
    role: str = Form(...),
    date: str = Form(...),
    notes: str = Form(""),
    status: str = Form("applied"),
    username: str = Form(...)
):
    data = load_data()
    application = {
        "company": company,
        "role": role,
        "date": date,
        "status": status.lower(),
        "notes": notes,
        "username": username
    }
    data.append(application)
    save_data(data)
    return RedirectResponse(url=f"/dashboard?username={username}", status_code=303)

# ✏️ Edit application
@app.post("/edit/{index}")
def edit_application(
    index: int,
    status: str = Form(...),
    notes: str = Form(""),
    username: str = Form(...)
):
    data = load_data()
    user_apps = [app for app in data if app["username"] == username]
    if 0 <= index < len(user_apps):
        real_index = [i for i, app in enumerate(data) if app["username"] == username][index]
        data[real_index]["status"] = status.lower()
        data[real_index]["notes"] = notes
        save_data(data)
    return RedirectResponse(url=f"/dashboard?username={username}", status_code=303)

# 🗑 Delete application
@app.post("/delete/{index}")
def delete_application(index: int, username: str = Form(...)):
    data = load_data()
    user_apps = [app for app in data if app["username"] == username]
    if 0 <= index < len(user_apps):
        real_index = [i for i, app in enumerate(data) if app["username"] == username][index]
        data.pop(real_index)
        save_data(data)
    return RedirectResponse(url=f"/dashboard?username={username}", status_code=303)


# Initialize data file on startup
init_data_file()
