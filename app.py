from flask import Flask, render_template, request, jsonify
from agent import handle_message
from utils import load_data

app = Flask(__name__)

# Load data on startup with error handling
try:
    pilots, drones, missions = load_data()
except Exception as e:
    print(f"Error loading data: {e}")
    pilots, drones, missions = None, None, None  # Fallback to None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global pilots, drones, missions
    if pilots is None or drones is None or missions is None:
        return jsonify({'response': 'Error: Unable to load data from Google Sheets. Check credentials.'})
    data = request.get_json()
    message = data.get('message', '')
    try:
        response, pilots, drones, missions = handle_message(message, pilots, drones, missions)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'Error processing message: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
