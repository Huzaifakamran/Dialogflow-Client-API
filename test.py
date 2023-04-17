from flask import Flask, request, jsonify
import google.cloud.dialogflow_v2 as dialogflow
import os

#Download the json key file from GCP with Dialogflow API client role And paste in the same directory  
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'hotel-book-2d76a-f8d8301046ea.json' 
                                                                                      


def detect_intent(user_id, user_message):
    session_client = dialogflow.SessionsClient()
    PROJECT_ID = 'hotel-book-2d76a'
    session_id = user_id
    session_path = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.types.TextInput(text=user_message, language_code='en-US')
    query_input = dialogflow.types.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session_path, query_input=query_input)
    # print(response)
    print(response.query_result.fulfillment_text)
    return response.query_result.fulfillment_text

user_id = 123
user_message = 'Hi'
    # Send user message to Dialogflow and get response
response = detect_intent(user_id, user_message)
