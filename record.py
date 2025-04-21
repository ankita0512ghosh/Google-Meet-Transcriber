#!/usr/bin/python3.10

import pyaudio
import wave
import signal
import sys
import os

# stop recording and write to output.wav
def cleanup():
    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

# if stop recording detected
def signal_handler(sig, frame):
    print('stopped recording')
    cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 30
WAVE_OUTPUT_FILENAME = os.path.join(os.path.dirname(__file__), "output.wav")

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("started recording")

frames = []

STOP_FLAG_PATH = os.path.join(os.path.dirname(__file__), "stop_recording.flag")

# record until flag file is created
try:
    while not os.path.exists(STOP_FLAG_PATH):
        data = stream.read(CHUNK)
        frames.append(data)
except KeyboardInterrupt:
    pass
finally:
    print('stopped recording')
    cleanup()
