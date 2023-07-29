from flask import Flask, request
from llm import final_run
from function import send_message

app = Flask(__name__)

@app.route('/')
def home():
    return 'No errors...'

@app.route('/twilio/receiveMessage', methods=['POST'])
def receiveMessage():
    try:
        # Extract incomng parameters from Twilio
        message = request.form['Body']
        sender_id = request.form['From']

        final_run(query=message)
        # result = get_response(message)
        # # result = text_complition(message)
        # if result['status'] == 1:
        #     send_message(sender_id, result['response'])

        send_message(sender_id, final_run)
    except:
        pass
    return 'OK', 200