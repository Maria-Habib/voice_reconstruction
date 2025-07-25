from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from models.whisper_utils import transcribe_audio
from models.tts_utils import generate_tts
###
app = FastAPI()

#DATA_PATH = "data/results.json"
AUDIOS_PATH = "/mount/src/voice_reconstruction/uclass_v1"
SAVE_DIR = "/mount/src/voice_reconstruction/saved_labels_uclass1.json"
LANGUAGE = 'en'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/transcribe")
def transcribe(file_path: str = Query(..., description="Full path to the audio file")):
    import os

    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    try:
        # 1. Transcribe using Whisper or your ASR model
        transcription = transcribe_audio(file_path)

        # 2. Generate TTS using XTTS or your model
        tts_audio = generate_tts(transcription, file_path)

        return {
            "transcription": transcription,
            "tts_audio": tts_audio  # Could be URL, path, or base64
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


'''
@app.get("/transcribe/{audio_name}")
def get_transcription(audio_name: str):
    path = os.path.join(AUDIOS_PATH, audio_name)
    print("ppppppppppppp", path)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=f"Audio file '{audio_name}' not found.")

    try:
        transcription = transcribe_audio(path, lang=LANGUAGE)
        tts_audio_path = generate_tts(transcription, audio_name, lang=LANGUAGE)
        return {"transcription": transcription, "tts_audio": tts_audio_path}
    except Exception as e:
        print("transcription error:", e)



@app.get("/transcribe/{audio_name}")
def get_transcription(audio_name: str):
    path = f"{AUDIOS_PATH}/{audio_name}"
    print("ppppppppppppp", path)
    try:
        transcription = transcribe_audio(path, lang=LANGUAGE)
        tts_audio_path = generate_tts(transcription, audio_name, lang=LANGUAGE)
    except Exception as e:
        print("trannscription errorrrrr", e)

    return {"transcription": transcription, "tts_audio": tts_audio_path}
'''


class LabelData(BaseModel):
    audio_name: str
    user_label: str
    annotator: str
    mother_tongue: str


@app.post("/save_label")
async def save_label(data: LabelData):
    try:
        # Save the label to a JSON file
        with open(SAVE_DIR, "a") as f:
            json.dump(data.dict(), f)
            f.write("\n")
        return {"message": "Label saved successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
