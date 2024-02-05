import json
import time
import os

from flask import Flask, request
from flask_sock import Sock
from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client

from azure_speech import AzureSpeechRecognizer, AzureSpeechSynthesizer, send_raw_audio
# from chatgpt_chat import get_response
from ollama_chat import OllamaChat
from openai_chat import OpenAIChat

from chat_history import ChatHistory
USER = 'USER:'
AI = 'AI:'
sentence_endings = [".", "!", "?", ":", "。", "！", "？", "："]

app = Flask(__name__)
sock = Sock(app)
twilio_client = Client()
speech_recognizer = AzureSpeechRecognizer()
speech_synthesizer = AzureSpeechSynthesizer()

@app.route('/', methods=['POST', 'GET'])
def call():
    """Accept a phone call."""
    response = VoiceResponse()
    # response.say("Hello, how may I assist you?")

    start = Connect()
    response.append(start)
    start.stream(url=f'wss://{request.host}/stream')

    return str(response), 200, {'Content-Type': 'text/xml'}

@sock.route('/stream')
def stream(ws):
    """Receive and recognize audio stream."""
    chat_history = ChatHistory(capacity=50)
    while ws.connected:
        message = ws.receive()
        packet = json.loads(message)      
        if packet["event"] == "start":
            welcome_wav_path = "welcome.wav"
            # if the welcome.wav file does not exist, create it
            if not os.path.exists(welcome_wav_path):
                text = "Hello, I am a chatbot, how may I assist you?"
                speech_synthesizer.text_to_wav(text, welcome_wav_path)
            print('\nStreaming has started')
            send_raw_audio(welcome_wav_path, ws, packet["streamSid"])

        elif packet['event'] == 'stop':
            print('\nStreaming has stopped')

        elif packet['event'] == 'media':
            data = packet["media"]["payload"]
            speech_recognizer.process_twilio_audio(f'{{"data": "{data}"}}')
            last_recognition = str(speech_recognizer.recognitions[-1])

            # if last_recognition contains any comma, period, exclaimation mark, question mark, or colon in either english or chinese it is a complete sentence
            if last_recognition != "" and any([c in last_recognition for c in sentence_endings]):
                user_request = last_recognition
                # 
                # remove the last recognition from the list
                speech_recognizer.recognitions.pop()
                # print("Recognized:", user_request)
                import asyncio
                # chatbot = OllamaChat()
                chatbot = OpenAIChat()

                async def on_chat(message):
                    # remove all the white spaces from the beginning and the end of the message
                    message = message.strip()
                    # if AI is i the message, remove AI from the message before sending it to the user
                    if message.startswith(AI):
                        message = message[len(AI):]
                    if message == "":
                        return
                    # get the current timestamp and use it in the file path
                    timestamp = str(int(time.time()))
                    wav_path = "output-" + packet["streamSid"] + "-" + timestamp + ".wav"
                    send_audio_stream(ws, message, packet["streamSid"], wav_path)
                    chat_history.put(AI + message)

                chat_history.put(USER + user_request)
                prompt = chat_history.string()    
                asyncio.run(chatbot.chat(prompt, callback=on_chat))

            if speech_recognizer.recognitions[-5:] == [""] * 10:
                print("No speech detected, stopping")
                ws.connected = False

def send_audio_stream(ws, response, stream_sid, wav_path):
    # split response to segments by comma, period, exclaimation mark, question mark, or colon
    # send each segment to the user
    segments = []
    segment = ""
    for c in response:
        segment += c
        if c in [",", ".", "!", "?", ":"]:
            segments.append(segment)
            segment = ""
    if segment:
        segments.append(segment)
    for segment in segments:
        print("Speak:", segment)
        speech_synthesizer.text_to_wav(segment, wav_path)
        try:
            send_raw_audio(wav_path, ws, stream_sid)
        except Exception as e:
            print(e)
        os.remove(wav_path)
        
if __name__ == '__main__':
    port = 9999
    if False:
        from pyngrok import ngrok
        public_url = ngrok.connect(port, bind_tls=True).public_url
        number = twilio_client.incoming_phone_numbers.list()[0]
        number.update(voice_url=public_url + '/call')
        print(f'Waiting for calls on {number.phone_number} public url: {public_url}')

    app.run(port=port)