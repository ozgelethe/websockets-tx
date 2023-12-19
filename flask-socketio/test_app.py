import time
import threading
import requests
import pytest
from flask import Flask
from flask.testing import FlaskClient

# Import the app and socketio from your app.py
from app import app, socketio, get_currency_values

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    return client

@pytest.fixture
def socketio_client():
    client = socketio.test_client(app)
    return client


def wait_for_event(socketio_client, event_name, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        received_events = socketio_client.get_received()
        for event in received_events:
            if event['name'] == event_name:
                return event['args'][0]
        time.sleep(0.1)
    raise TimeoutError(f"Timed out waiting for '{event_name}' event")

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'WebSocket Example' in response.data

def test_currency_update(socketio_client):

    # Emit the 'update_currencies' event to the app
    btc_value = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json').json()['bpi']['USD']['rate']
    
    socketio_client.emit('update_currencies', {'BTC': btc_value})

    # Print received events for debugging
    received_events = socketio_client.get_received()
    print("Received Events:", received_events)

    # Wait for the 'update_currencies' event
    try:
        data = wait_for_event(socketio_client, 'update_currencies', timeout=10)
    except TimeoutError as e:
        # Print more information to diagnose the issue
        print("TimeoutError:", e)
        print("Received Events after Timeout:", socketio_client.get_received())
        raise

    print("Received Data:", data)
    assert data is not None

    initial_btc_value = data['BTC']

    time.sleep(7)  # Adjust the timing as needed

    # Wait for the 'update_currencies' event after the second update
    try:
        data = wait_for_event(socketio_client, 'update_currencies', timeout=30)
    except TimeoutError as e:
        # Print more information to diagnose the issue
        print("TimeoutError:", e)
        print("Received Events after Timeout:", socketio_client.get_received())
        raise

    print("Received Data:", data)
    assert data is not None

    updated_btc_value = data['BTC']

    assert initial_btc_value is not None
    assert updated_btc_value is not None
    assert initial_btc_value != 'Loading...'
    assert updated_btc_value != 'Loading...'
    assert initial_btc_value != updated_btc_value
