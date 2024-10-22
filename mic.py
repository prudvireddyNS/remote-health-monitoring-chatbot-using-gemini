import speech_recognition as s
recognizer=s.Recognizer()
def hear():
    with s.Microphone() as source:
        print("Say Something")
        recognizer.adjust_for_ambient_noise(source)
        audio =recognizer.listen(source)
        print("Recognizing..")
        text=recognizer.recognize_google(audio)
    return text

