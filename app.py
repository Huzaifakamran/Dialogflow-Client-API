from flask import Flask, request, jsonify,render_template
from google.cloud import dialogflow
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
   return render_template('index.html')

@app.route('/address', methods=['POST'])
def address():
    address = request.json
    print(address['address']['formatted_address'])
    return 'received'

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_message = request.json['message']
    print(user_message)
    print(user_id)
    user_id = request.args.get('user_id')

    # Send user message to Dialogflow and get response
    response = detect_intent(user_id, user_message)

    # Return bot response
    return jsonify({'message': response})

def detect_intent(user_id, user_message):
    session_client = dialogflow.SessionsClient()
    PROJECT_ID = 'hotel-book-2d76a'
    session_id = f'projects/{PROJECT_ID}/agent/sessions/{user_id}'
    session = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.types.TextInput(text=user_message, language_code='en-US')
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)

    return response.query_result.fulfillment_text

if __name__ == '__main__':
    app.run(debug=True)