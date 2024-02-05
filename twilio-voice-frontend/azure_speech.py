import json
import os
import threading
import wave
import base64
import audioop
import soundfile

from dotenv import load_dotenv
_ = load_dotenv('config.env')

# based on https://medium.com/@atgorvi/twilio-voice-chat-assistant-using-azure-speech-recognition-and-python-efaf6319b583
import azure.cognitiveservices.speech as speechsdk
from azure.cognitiveservices.speech import SpeechSynthesizer, AudioConfig

class AzureSpeechRecognizer:
    key = os.environ["AZURE_SPEECH_KEY"]
    service_region = os.environ["AZURE_SPEECH_REGION"]

    def __init__(self):
        audio_format = speechsdk.audio.AudioStreamFormat(samples_per_second=8000, bits_per_sample=16,
                                                         channels=1, wave_stream_format=speechsdk.AudioStreamWaveFormat.MULAW)
        self.stream = speechsdk.audio.PushAudioInputStream(stream_format=audio_format)
        self.audio_config = speechsdk.audio.AudioConfig(stream=self.stream)
        self.recognition_done = threading.Event()
        
        # Adjust silence detection time limit
        initial_silence_timeout_ms = 10 * 1e3
        end_silence_timeout_ms = 10 * 1e3  # Example value: 10 seconds
        babble_timeout_ms = 10 * 1e3  # Example value: 10 seconds
        end_silence_timeout_ambiguous_ms = 10 * 1e3  # Example value: 10 seconds
        template = ("wss://{}.stt.speech.microsoft.com/speech/recognition"
                    "/conversation/cognitiveservices/v1?initialSilenceTimeoutMs={:d}"
                    "&endSilenceTimeoutMs={:d}&babbleTimeoutMs={:d}&endSilenceTimeoutAmbiguousMs={:d}")

        endpoint = template.format(self.service_region, int(initial_silence_timeout_ms), int(end_silence_timeout_ms),
                                   int(babble_timeout_ms), int(end_silence_timeout_ambiguous_ms))

        self.speech_config = speechsdk.SpeechConfig(subscription=self.key, endpoint=endpoint, speech_recognition_language="en-US")
        self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config, audio_config=self.audio_config)

        self.recognitions = [""]

        self.speech_recognizer.recognizing.connect(self.recognizing_cb)
        self.speech_recognizer.recognized.connect(self.recognized_cb)
        self.speech_recognizer.session_stopped.connect(self.session_stopped_cb)
        self.speech_recognizer.canceled.connect(self.canceled_cb)

        self.recognize_thread = threading.Thread(target=self.recognize_audio)
        self.recognize_thread.start()

    def session_stopped_cb(self, evt):
        print('SESSION STOPPED: {}'.format(evt))
        self.recognition_done.set()

    def canceled_cb(self, evt):
        #print('CANCELED: {}'.format(evt.reason))
        self.recognition_done.set()

    def recognizing_cb(self, evt):
        #print(f"RECOGNIZING: {evt}")
        pass

    def recognized_cb(self, evt):
        print('RECOGNIZED:', evt.result.text)
        self.recognitions.append(evt.result.text)

    def push_audio(self, audio_data):
        audio_bytes = base64.b64decode(audio_data.get("data", "").encode())
        self.stream.write(audio_bytes)

    def recognize_audio(self):
        self.speech_recognizer.start_continuous_recognition()
        self.recognition_done.wait()
        self.speech_recognizer.stop_continuous_recognition()

    def process_twilio_audio(self, twilio_audio_json):
        audio_data = json.loads(twilio_audio_json)
        self.push_audio(audio_data)


class AzureSpeechSynthesizer:
    key = os.environ["AZURE_SPEECH_KEY"]
    service_region = os.environ["AZURE_SPEECH_REGION"]

    def __init__(self):

        self.speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.service_region, speech_recognition_language="en-US")
        self.speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff8Khz8BitMonoMULaw)
        # self.speech_config.speech_synthesis_voice_name = ""

        self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

    def text_to_wav(self, text: str, file_name: str = "output.wav"):
        audio_output = AudioConfig(filename=file_name)
        synthesizer = SpeechSynthesizer(speech_config=self.speech_config, audio_config=audio_output)
        synthesizer.speak_text_async(text).get()

def send_raw_audio(file_path, ws, stream_sid):
    data, samplerate = soundfile.read(file_path)
    soundfile.write(file_path, data, samplerate)
    with wave.open(file_path, 'rb') as wav_file:
        while True:
            wav_data = wav_file.readframes(320)
            if wav_data and len(wav_data) > 0:
                mulaw_data = audioop.lin2ulaw(wav_data, 2)
                base64_audio = base64.b64encode(mulaw_data).decode("utf-8")
                msg = {
                    "event": "media",
                    "streamSid": stream_sid,
                    "media": {
                        "payload": base64_audio
                    }
                }
                # convert msg to json string
                json_msg = json.dumps(msg)
                # print("sending audio", json_msg)
                # send json string to websocket
                ws.send(json_msg)

            else:
                # print("No more audio to send")
                break
            if False: #if not wav_data:
                ws.send(
                    {
                        "event": "mark",
                        "streamSid": stream_sid,
                        "mark": {
                            "name": "my label"
                        }
                    }
                )
                break
            
            
            