import os
print("Loading Piper TTS...")
def synthesize_speech(text: str, output_path: str):
    try:
        from piper import PiperVoice
        voice_path = os.getenv("PIPER_VOICE", "en_US-lessac-medium.onnx")
        if os.path.exists(voice_path):
            voice = PiperVoice.load(voice_path)
            with open(output_path, "wb") as f:
                for audio in voice.synthesize(text):
                    f.write(audio.audio_int16_bytes)
            return output_path
    except Exception as e:
        print(f"Piper failed: {e}")
    try:
        import wave
        with wave.open(output_path,'w') as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(22050)
            wf.writeframes(b'\x00\x00'*11025)
    except:
        open(output_path,'wb').write(b'')
    return output_path
