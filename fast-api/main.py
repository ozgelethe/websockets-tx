# main.py
from fastapi import FastAPI, WebSocket, Request  # Import Request class
import httpx
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio

app = FastAPI()

# Serve static files (e.g., index.html) from the 'static' directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates directory for Jinja2
templates = Jinja2Templates(directory="templates")

async def fetch_bitcoin_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.coindesk.com/v1/bpi/currentprice/BTC.json")
        data = response.json()
        return data["bpi"]["USD"]["rate"]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        bitcoin_rate = await fetch_bitcoin_data()
        await websocket.send_text(f"Current Bitcoin Rate (USD): {bitcoin_rate}")
        await asyncio.sleep(10)  # Update every 60 seconds

# Define a route to render the index.html template
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
