from flask import Flask, render_template, request, jsonify
from agent import handle_message
from utils import load_data

app = Flask(__name__)

# Load data on startup
pilots, drones, missions = load_data()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global pilots, drones, missions
    data = request.get_json()
    message = data.get('message', '')
    response, pilots, drones, missions = handle_message(message, pilots, drones, missions)
    return jsonify({'response': response})

# Keep existing drone simulation routes if needed
# ...existing code...

if __name__ == '__main__':
    app.run(debug=True)
