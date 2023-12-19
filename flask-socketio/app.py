import time
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def get_currency_values():
    while True:
        # Replace this with your logic to fetch real-time currency values
        btc_value = requests.get('https://api.coindesk.com/v1/bpi/currentprice/BTC.json').json()['bpi']['USD']['rate']

        # Emit the currency values to all connected clients
        socketio.emit('update_currencies', {'BTC': btc_value})

        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    # Start a separate thread for getting currency values
    from threading import Thread
    currency_thread = Thread(target=get_currency_values)
    currency_thread.start()

    # Run the Flask app
    socketio.run(app)
