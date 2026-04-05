from __future__ import annotations

import threading
import wave

import pyaudio

from .config import VoiceConfig


def record_until_keypress(config: VoiceConfig, output_filename: str='output.wav'):
    """
    Records audio from the default microphone and saves it to a WAV file.
    The recording stops when the user presses the Enter key.
    """
    # Audio configuration
    CHUNK = 1024  # Number of audio frames per buffer
    FORMAT = pyaudio.paInt16  # 16-bit resolution
    CHANNELS = 1  # 1 channel (mono)

    audio = pyaudio.PyAudio()
    frames = []
    stop_event = threading.Event()

    def record():
        """Background task that actively records audio chunks."""
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=config.sample_rate,
            input=True,
            frames_per_buffer=CHUNK,
        )

        # Keep reading chunks of audio until the stop_event is triggered
        while not stop_event.is_set():
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()

    # Start the recording on a separate thread
    print('Recording started... Press [ENTER] to stop.')
    record_thread = threading.Thread(target=record)
    record_thread.start()

    # The main thread blocks here waiting for the user to press Enter
    input()

    # Once Enter is pressed, signal the background thread to stop and wait for it
    stop_event.set()
    record_thread.join()
    print(f"🛑 Recording stopped. Saving to '{output_filename}'...")

    # Terminate the PyAudio object
    audio.terminate()

    # Save the captured frames to a WAV file
    with wave.open(output_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(config.sample_rate)
        wf.writeframes(b''.join(frames))

    print('Save complete.')
