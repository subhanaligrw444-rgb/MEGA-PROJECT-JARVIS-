import pyttsx3

engine = pyttsx3.init()

print("=== Installed voices ===")
voices = engine.getProperty("voices")
for index, voice in enumerate(voices):
    print(index, "|", voice.name, "|", voice.id)

print("Current rate:", engine.getProperty("rate"))
print("Current volume:", engine.getProperty("volume"))

engine.say("Hello. I am Jarvis. Text to speech is working.")
engine.runAndWait()
print("Finished speaking.")