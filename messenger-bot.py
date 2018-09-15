## Python libraries that we need to import for our bot
import botUtil
from flask import Flask, request
from pymessenger.bot import Bot ## pymessenger is a Python wrapper for the Facebook Messenger API

app = Flask(__name__) ## This is how we create an instance of the Flask class for our app

ACCESS_TOKEN = 'EAAEXESyVKJkBAMQZAfEzTcFl70KAD7UVx9a53AWxHhjL6J1UdzaPUd1BcRfyuUkChP3xlZA3QMZAtZCuqzpjMVreHZAll6UaAZBypV6CkRTlLfgM0IxL5pF3CwGMF2mGdzwKe9GCgIl724bZCkZCtv8abszReP3ZBdL1r1m1kGJqVfRm5o9oB6hhK'
VERIFY_TOKEN = 'nmslwsnd' ## Replace 'VERIFY_TOKEN' with your verify token
bot = Bot(ACCESS_TOKEN) ## Create an instance of the bot
flag1 = False
flag2 = False
flag3 = False

def verify_fb_token(token_sent):
    ## Verifies that the token sent by Facebook matches the token sent locally
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

# Chooses a message to send to the user
def get_message_text():
    return "Hey, it looks like you're interested in HackRice! For more information, please visit http://hack.rice.edu"

## Send text message to recipient
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response) ## Sends the 'response' parameter to the user
    return "Message sent"

## This endpoint will receive messages
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    global flag1
    global flag2
    global flag3
    print("MESSAGE RECEIVED")

    m = botUtil.get_course_info()
    ## Handle GET requests
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token") ## Facebook requires a verify token when receiving messages
        return verify_fb_token(token_sent)

    ## Handle POST requests
    else:
        output = request.get_json() ## get whatever message a user sent the bot
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id'] ## Facebook Messenger ID for user so we know where to send response back to
                    ## If user sends text
                    if not flag1:
                        send_message(recipient_id, "Hi, I am here to help you with your course selection, please enter the courses you would like to take, splited by comma!")
                        flag1 = True
                    elif not flag2:
                        response_sent_text = message['message'].get('text').upper()
                        process = botUtil.check_valid(botUtil.get_courses_from_input(response_sent_text), m)
                        if not process:
                            send_message(recipient_id,
                                         "You typed in some course name incorrectly or the course names are not in the correct format!")
                        else:
                            send_message(recipient_id, botUtil.get_msg2send(response_sent_text, m))

                    # if "hackrice" in message['message'].get('text').lower():
                    #     response_sent_text = get_message_text()
                    #     send_message(recipient_id, response_sent_text)


    return "Message Processed"

## Ensures that the below code is only evaluated when the file is executed, and ignored if the file is imported
if __name__ == "__main__":
    app.run(port=80) ## Runs application