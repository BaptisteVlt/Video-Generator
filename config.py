from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Config:
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "1ns94GwK9YDCJoL6Nglv"
    ELEVENLABS_MODEL_ID: str = "eleven_multilingual_v2"
    OUTPUT_DIR: str = "./video_data/"
