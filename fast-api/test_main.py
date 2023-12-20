from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Bitcoin Currency App" in response.text


def test_websocket():
    with client.websocket_connect("/ws", timeout=10) as websocket:
        time.sleep(10)  # Allow the test to run for 10 seconds (adjust as needed)
        data = websocket.receive_text()
        assert "Current Bitcoin Rate (USD):" in data

