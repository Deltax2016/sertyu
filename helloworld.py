import logging
import os
from flask import Flask
from flask_ask import Ask, question, statement

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    speech_text = 'Hello, it is application for medicine consumption control'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.intent('HelloWorldIntent')
def hello_world():
    speech_text = 'You need to swallow 3  Parazitomol pills'
    return question(speech_text)

@ask.intent('HelloNameIntent', default = {'name':'world'})
def hello_world(name):
    speech_text = f'Hello, {name} , have  you  got  some  new regulations?'
    return question(speech_text)

@ask.intent('AMAZON.StopIntent')
def stop():
   speech_text = 'Goodbye world!'
   return statement(speech_text)

@ask.intent('AMAZON.HelpIntent')
def help():
    speech_text = 'You can say hello to me!'
    return question(speech_text).reprompt(speech_text).simple_card('HelloWorld', speech_text)

@ask.session_ended
def session_ended():
    return "{}", 200

if __name__ == '__main__':
   app.run(debug=True)

