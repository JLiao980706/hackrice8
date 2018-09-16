import botUtil
import courseUtil
from flask import Flask, request, make_response, render_template
from pymessenger.bot import Bot
import ast
from datetime import datetime

app = Flask(__name__)  # This is how we create an instance of the Flask class for our app

ACCESS_TOKEN = 'EAAGB4sIKbrQBACq3NTPiSdPJGY534iAR51nY1FqOgjyQLXRIAuH4DQAeQK0WEpNkr3ZCEnWVs9MBqSIbDuFwqsYiDirqTxZCBtkMIqQ92yqwgKo1RoQq0Au0jvDpac28SQk5Grqm4tIuZBVMwTUUIZBWZCEqszE4tQR6jBpqKaQZDZD'
VERIFY_TOKEN = 'nmslwsnd'  # Replace 'VERIFY_TOKEN' with your verify token
bot = Bot(ACCESS_TOKEN)  # Create an instance of the bot
yes0 = False
flag_intro = False
flag_major = False
flag_year = False
flag0 = False
flag1 = False
flag2 = False
flag3 = False
m = botUtil.get_course_info()
m2 = botUtil.get_pre_req()
course_list = []
course_taken = []

if datetime.now().month < 9:
    cTerm = "S"
    currentTerm = "Spring"
    nextTerm = "Fall"
else:
    cTerm = "F"
    currentTerm = "Fall"
    nextTerm = "Spring"


def verify_fb_token(token_sent):
    # Verifies that the token sent by Facebook matches the token sent locally
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# Send text message to recipient
def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "Message sent"


# This endpoint will receive messages
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    global flag_intro
    global flag_major
    global flag_year
    global yes0
    global flag0
    global flag1
    global flag2
    global flag3
    print("MESSAGE RECEIVED")
    global course_list
    global course_taken
    global m2
    global m
    # Handle GET requests
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")  # Facebook requires a verify token when receiving messages
        return verify_fb_token(token_sent)

    # Handle POST requests
    else:
        output = request.get_json()  # get whatever message a user sent the bot
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    recipient_id = message['sender']['id']  # Facebook Messenger ID for user so we know where to send response back to
                    # If user sends text
                    if not flag_intro:
                        intro = "Hi! This is your personal Rice Academic Helper. This is now the {} semester so I will help you with your Spring course selection".format(currentTerm)
                        send_message(recipient_id, intro)
                        send_message(recipient_id, "May I know your major?")
                        flag_intro = True

                    elif not flag_major:
                        response_sent_text = message['message'].get('text').upper()
                        if response_sent_text == "CS" or response_sent_text == "COMPUTER SCIENCE":
                            send_message(recipient_id, "Great!")
                            flag_major = True
                            send_message(recipient_id, "Which year student are you? 1, 2, 3 or 4?")
                        else:
                            send_message(recipient_id, "Sorry, we don't have full supports for other majors right now. Stay tight for updates!")

                    elif not flag_year:
                        response_sent_text = message['message'].get('text').upper()
                        try:
                            year = int(response_sent_text)
                            year_map = {1: "freshman", 2: "sophomore", 3: "junior", 4: "senior"}
                            send_message(recipient_id, "Gotcha! So you are a {}".format(year_map[year]))
                            text = "Please use the link below to enter all the major courses you have taken."
                            bot.send_button_message(recipient_id, text, buttons=[{
                                "type": "web_url",
                                "url": "https://fced6db5.ngrok.io/class/" + recipient_id,
                                "title": "Enter your courses",
                                "webview_height_ratio": "tall",
                                "messenger_extensions": True
                            }])
                            flag_year = True
                        except ValueError:
                            send_message(recipient_id, "Sorry, I can't understand what you said.")

                    elif not yes0:
                        if flag0:
                            if "yes" == message['message'].get('text').lower() or "y" == message['message'].get(
                                    'text').lower():
                                yes0 = True
                                send_message(recipient_id,
                                             "Please enter the courses you would like to take next semester, split by comma!")

                        if not yes0:
                            text = "Please use the link below to re-enter all the major courses you have taken."
                            bot.send_button_message(recipient_id, text, buttons=[{
                                "type": "web_url",
                                "url": "https://fced6db5.ngrok.io/class/" + recipient_id,
                                "title": "Enter your courses",
                                "webview_height_ratio": "tall",
                                "messenger_extensions": True
                            }])
                    # elif not flag1:
                    #     send_message(recipient_id, "Please enter the courses you would like to take, split by comma!")
                    #     flag1 = True
                    elif not flag2:
                        response_sent_text = message['message'].get('text').upper()
                        process, reason = botUtil.check_valid(botUtil.get_courses_from_input(response_sent_text), m, cTerm)
                        if not process:
                            if reason == 1:
                                send_message(recipient_id,
                                            "You did not type course names separated by comma, or the course names are not in the correct format!")
                            else:
                                send_message(recipient_id,
                                             "The course you entered is not offered in {}".format(nextTerm))
                        else:
                            course_list = botUtil.get_courses_from_input(response_sent_text)
                            send_message(recipient_id, botUtil.get_msg2send(response_sent_text, m, m2, course_taken))
                            flag2 = True
                    elif not flag3:
                        response_sent_text = message['message'].get('text').upper()
                        if "COURSE RECOMMENDATION" in response_sent_text:
                            tuple_of_tuple = botUtil.course_recommandation(course_list, m, course_taken, botUtil.readin_json("course_graph.json"), botUtil.readin_json("course_cat.json"))
                            send_message(recipient_id, botUtil.check_major_pre_req(course_list, botUtil.readin_json("pre_req.json"), course_taken))
                            send_message(recipient_id, courseUtil.tpt_to_output_string(tuple_of_tuple))
                            break
                        process, reason = botUtil.check_valid(botUtil.get_courses_from_input(response_sent_text), m, cTerm)
                        if process:
                            send_message(recipient_id, botUtil.get_msg2send(response_sent_text, m, m2, course_taken))
                            course_list = botUtil.get_courses_from_input(response_sent_text)
                        else:
                            output_list, idx = courseUtil.get_add_subtract_list(response_sent_text, m)
                            if not output_list[idx]:
                                if idx == 1:
                                    send_message(recipient_id, "The course you want to add may not be a valid course"
                                                               " or the course is not available in this semester.\n")
                                    continue
                                elif idx == 2:
                                    send_message(recipient_id, "The course you want to remove may not be a valid course"
                                                               " or the course is not available in this semester.\n")
                                    continue
                            for itm in output_list[0]:
                                send_message(recipient_id, "What do you want to do with " + itm + "?\n")
                            for itm in output_list[1]:
                                if itm not in course_list:
                                    send_message(recipient_id, "Added " + itm + ".\n")
                                    course_list.append(itm)
                                else:
                                    send_message(recipient_id, itm + " is already in your choices!\n")
                            for itm in output_list[2]:
                                if itm in course_list:
                                    send_message(recipient_id, "Removed " + itm + ".\n")
                                    course_list.remove(itm)
                                else:
                                    send_message(recipient_id, "You have not chosen " + itm + "!\n")
                            send_message(recipient_id, "\n")
                            send_message(recipient_id, "Analyzing your new course selection: ")
                            send_message(recipient_id, botUtil.get_msg2send_from_list(course_list, m, m2, course_taken))

    return "Message Processed"


@app.route("/class/<recipient_id>", methods=['GET', 'POST'])
def get_classes_taken(recipient_id):
    print(recipient_id)
    referrer = request.environ['HTTP_REFERER']
    res = make_response(render_template("form.html", value=recipient_id))
    if 'facebook.com' in referrer:
        res.headers.set('X-Frame-Options', 'ALLOW-FROM https://www.facebook.com/')
    elif 'messenger.com' in referrer:
        res.headers.set('X-Frame-Options', 'ALLOW-FROM https://www.messenger.com/')
    return res


@app.route("/class-result", methods=['GET', 'POST'])
def get_form_result():
    data = request.data.decode('utf8').replace("'", '"')
    my_json = ast.literal_eval(data)
    print(my_json)
    if len(my_json['course']) == 0:
        course = "NO CLASS"
    else:
        course = ', '.join(my_json['course'])
    send_message(my_json['recipient_id'], "You have taken " + course + ". Right? Say YES to confirm")
    global flag0
    global course_taken
    course_taken = [itm.replace(" ", "") for itm in my_json["course"]]

    flag0 = True

    return "Result Got!"


if __name__ == "__main__":
    app.run()