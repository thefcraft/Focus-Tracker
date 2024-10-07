from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/active-tab', methods=['POST'])
def active_tab():
    data = request.json
    url = data.get('url')
    print(f"Active tab URL: {url}")
    return 'Received', 200

if __name__ == '__main__':
    app.run(port=7853)