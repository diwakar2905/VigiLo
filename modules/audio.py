# modules/audio.py
import os
import time
from modules.base import BaseModule
from logs.logger import logger

class AudioModule(BaseModule):
    def execute(self, save_dir, duration=5, prefix="audio_"):
        """
        Records duration seconds of audio from the default microphone and saves it as a WAV file.
        Returns the absolute filepath if successful, or None.
        """
        try:
            import pyaudio
            import wave
            
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            try:
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            except Exception as se:
                logger.error(f"Failed to open audio input stream: {se}")
                p.terminate()
                return None
                
            logger.info(f"Recording {duration} seconds of audio...")
            frames = []
            
            # Read chunks
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
                
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            filename = f"{prefix}{int(time.time())}.wav"
            filepath = os.path.join(save_dir, filename)
            
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"Audio recorded successfully: {filepath}")
            return filepath
        except ImportError:
            logger.error("pyaudio is not installed on the system.")
        except Exception as e:
            logger.error(f"Audio module exception: {e}")
            
        return None
