# DeskmateAI

DeskmateAI is a voice-controlled desktop assistant for Windows. You say a wake word, speak a command in English, Hindi or Marathi, and it carries out the action on your PC: opening apps, changing volume, controlling media, clicking things on screen, typing text, and so on. Speech recognition, intent classification and translation all run locally, so it works without an internet connection once the models are on disk.

Access is tied to the user. Logging in can be done with a password, a voice passphrase or face recognition, and spoken commands are checked against the registered speaker's voice.

## Features

- Wake word detection (default: "hey deskmate", configurable per user)
- Speech recognition with a Whisper small model running through faster-whisper
- Hindi and Marathi commands translated to English before processing (Helsinki-NLP Opus-MT)
- Two-stage intent classification: a fast Sentence-BERT match first, with a local LLM (phi3.5 through Ollama) as fallback
- Self-learning: commands the LLM classifies are saved, so the next occurrence is handled by SBERT directly
- Undo and redo for executed actions
- Dictation mode for typing out longer text by voice
- Click-by-description: say what is on screen and it finds and clicks it using EasyOCR
- Spoken replies through offline text-to-speech (pyttsx3), in the user's chosen language
- Multi-user registration with password, voice and face authentication, plus per-command speaker verification
- System tray app with a login window, dashboard and settings

## Supported commands

The intent set currently has 39 intents, grouped roughly as follows.

| Area | Examples |
|---|---|
| Apps | open app, close app, switch window |
| Web | search, new tab, close tab, zoom in/out |
| Sound and display | volume up/down, mute/unmute, brightness up/down |
| Media | play, pause, next, previous |
| System | shutdown, restart, sleep, lock, screenshot |
| Windows | minimize, maximize, close, hide |
| Editing | write text, copy, paste, select all, save, undo, redo |
| Navigation | scroll up/down, click an element |
| DeskmateAI itself | open dashboard, open settings |

The full list with example phrases is in `NLP/nlp/intents/intent_examples.json`.

## How it works

```
wake word -> speech recognition -> translation (hi/mr -> en)
          -> intent classification (SBERT, then LLM fallback)
          -> authentication check -> command execution -> spoken response
```

1. **Wake word.** A background listener transcribes short audio chunks with the Whisper model and triggers when it hears the wake word.
2. **Speech recognition.** Audio is cleaned up (noise reduction, normalisation, silence trimming) and transcribed by a fine-tuned multilingual Whisper small model, converted to CTranslate2.
3. **Translation.** Hindi and Marathi text is translated to English. English passes straight through.
4. **Intent classification.** `all-MiniLM-L6-v2` embeddings are compared against the stored examples for each intent. If the best score is below 0.50, the command goes to phi3.5 on Ollama instead. Whatever the LLM decides is written to `intent_memory.json`.
5. **Authentication.** The speaker is verified against the registered voice embeddings before the command runs.
6. **Execution.** The command registry maps the intent to a handler. Automation tries pyautogui first, then pywinauto, then ctypes as a last resort.
7. **Response.** The result is spoken back and the tray icon reflects the current state (idle, wake word, listening, processing, muted).

## Project structure

```
main.py                     entry point
install.bat                 dependency installer (Windows)
requirements.txt
test_suite.py               import and logic tests, no models or mic needed

NLP/
  nlp/                      SBERT engine, LLM fallback, intent pipeline, intent data
  speech/
    asr/                    Whisper loader, microphone stream, speech handler
    preprocessing/          noise reduction, normalisation, silence trimming
    wakeword/               wake word detector
  translation/              Hindi/Marathi to English
  models/                   local model files (not in the repo)

backend/
  core/                     pipeline, registry, executor, context, memory, learner, undo/redo, responder
  automation/               app launcher, media, system, UI clicking and typing, web, workflows
  security/                 auth orchestrator, password, voice, face, registration, sessions
  utils/                    logging and helpers
  data/                     per-user profiles and logs (created at runtime)

ui/
  controller.py             bridge between the UI and the pipeline
  tray_icon.py              system tray icon and menu
  animations/               status indicator, waveform
  views/                    login, register, dashboard, settings, main window
```

## Requirements

- Windows 10 or 11 (the automation layer uses pywin32, pycaw and pywinauto)
- Python 3.10 or newer
- A microphone, and a webcam if you want face login
- [Ollama](https://ollama.com) installed and on your PATH, with the `phi3.5` model pulled
- An NVIDIA GPU is recommended. The ASR loader is currently set to CUDA with float16.

## Installation

```bash
git clone https://github.com/Shubh-Pi/DeskmateAI.git
cd DeskmateAI
python -m venv venv
```

Then run the installer, which installs the dependencies in a specific order to avoid numpy and OpenCV version conflicts:

```bat
install.bat
```

Pull the LLM used for fallback classification:

```bash
ollama pull phi3.5
```

### Models

Model files are too large for the repository and are ignored by git. Place them as follows before the first run:

| Path | Contents |
|---|---|
| `NLP/models/whisper/` | Whisper small in CTranslate2 format |
| `NLP/models/sbert/` | `all-MiniLM-L6-v2` (optional; it is downloaded if the folder is empty) |
| `NLP/models/translation/` | Opus-MT hi-en and mr-en (downloaded on first use) |

If you have Whisper weights in Hugging Face format, `convert.py` converts them to CTranslate2 with int8 quantisation. Edit the paths at the top of the script first.

## Running

```bash
python main.py
```

DeskmateAI starts Ollama if it is not already running, loads the models, and puts an icon in the system tray. Register a user from the login window, then say the wake word followed by a command.

## Tests

```bash
python test_suite.py
```

The suite checks that every module imports, that classes instantiate, and that core logic behaves. It reports PASS, FAIL or SKIP for each check and does not need models, a microphone or a GPU.

## Privacy

- Recognition, translation and classification all run on your machine.
- Voice and face data are stored as embeddings (`.npy` files) under `backend/data/users/`, not as raw audio or images. That folder is git-ignored and should stay out of version control.
- Passwords are hashed with bcrypt.
- Screenshots used for click-by-description are held in memory and not written to disk.
- Sessions live in memory only, so you log in again after a restart.

## Known limitations

- Windows only.
- Hindi and Marathi are the only non-English languages supported.
- Click-by-description works on the active window and depends on OCR accuracy.
- Whisper and Ollama together need a fair amount of RAM; first startup is slow while models load.

## License

Add a license here.
