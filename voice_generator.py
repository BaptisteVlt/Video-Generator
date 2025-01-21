from elevenlabs import ElevenLabs, save
import os
from models import QuizSection
from config import Config

class VoiceGenerator:
    def __init__(self, config: Config, OUTPUT_VOICE_DIR: str):
        self.client = ElevenLabs(api_key=config.ELEVENLABS_API_KEY)
        self.config = config
        self.OUTPUT_VOICE_DIR = OUTPUT_VOICE_DIR

    def create_voice(self, text: str, filename: str) -> None:
        if not os.path.exists(self.OUTPUT_VOICE_DIR):
            os.makedirs(self.OUTPUT_VOICE_DIR)

        output_file = os.path.join(self.OUTPUT_VOICE_DIR, filename)

        response = self.client.text_to_speech.convert(
            voice_id=self.config.ELEVENLABS_VOICE_ID,
            text=text,
            model_id=self.config.ELEVENLABS_MODEL_ID
        )
        save(response, output_file)

    def generate_all_voices(self, quiz: QuizSection) -> None:
        voice_parts = {
            'Introduction.mp3': quiz.introduction,
            'Appel.mp3': quiz.appel_abonnement
        }

        # Add questions and responses
        for num in range(1, len(quiz.questions) + 1):
            voice_parts[f'Question_{num}.mp3'] = quiz.questions[f'question_{num}']
            voice_parts[f'Reponse_{num}.mp3'] = quiz.reponses[f'reponse_{num}']

        # Generate all voice files
        for filename, text in voice_parts.items():
            self.create_voice(text, filename)
