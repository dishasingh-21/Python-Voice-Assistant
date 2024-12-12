import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Say something!")
    try:
        audio = recognizer.listen(source, timeout=5)
        print("Audio captured successfully!")
        said = recognizer.recognize_google_cloud(audio)
        print(said)
    except Exception as e:
        print(f"Error capturing audio: {e}")