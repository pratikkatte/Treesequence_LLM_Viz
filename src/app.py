from flask import Flask, request, jsonify, Response
from langgraph_tskit import api_interface
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

class DataStreamer:
    def __init__(self):
        self.json_data = {"message": "", "status": "Updated"}

    def stream_data(self):
        while True:
            # with open("file.txt", 'r') as file:
            #     data = file.read().strip()

            # self.json_data["message"] = data'
            yield f"data: {json.dumps(self.json_data)}\n\n"

data_streamer = DataStreamer()

@app.route('/api/stream')
def stream():
    return Response(data_streamer.stream_data(), content_type='text/event-stream')

# Test GET endpoint
@app.route('/', methods=['GET'])
def status():
    print("Status endpoint accessed")
    return "Success 200!"

# Define the /api/chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()  # Get the JSON data from the request
    message = data.get('message')

    llm_output, llm_visual = api_interface(message)

    data_streamer.json_data['message'] = llm_visual
    
    
    # Process the incoming message here (for now, we simply return it)
    print(f"Response message: {llm_output}")

    # Respond with a simple JSON response
    return jsonify({"response": f"{llm_output}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

