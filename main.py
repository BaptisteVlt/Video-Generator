from config import Config
from quiz_generator import QuizGenerator
from voice_generator import VoiceGenerator
from image_generator import ImageGenerator
from montage import create_educational_video
import os
from datetime import datetime
import json
from dataclasses import asdict
import logging
from typing import Optional
from pathlib import Path

class QuizApp:
    def __init__(self):
        self.setup_logging()
        self.config = Config()
        self.date_str = datetime.now().strftime("%m-%d-%y")
        self.base_output_dir = self._setup_output_directory()

    def setup_logging(self):
        """Configure logging with rotating file handler"""
        log_file = "app.log"
        logging.basicConfig(
            filename=log_file,
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def _setup_output_directory(self) -> Path:
        """Create and return the base output directory"""
        output_dir = Path(self.config.OUTPUT_DIR) / self.date_str
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created output directory: {output_dir}")
        return output_dir

    def _create_subdirectory(self, subdir: str) -> Path:
        """Create and return a subdirectory in the output directory"""
        path = self.base_output_dir / subdir
        path.mkdir(exist_ok=True)
        return path

    def get_user_input(self) -> tuple[str, str]:
        """Get and validate user input"""
        quiz_type = input("Quel type de quiz voulez-vous générer aujourd'hui ? (Science, Histoire, Geographie ou General) ").strip()
        num_questions = input("Combien de questions voulez-vous générer ? ").strip()
        
        if quiz_type not in ['Science', 'Histoire', 'Geographie', 'General'] or not num_questions.isdigit():
            raise ValueError("Le type de quiz ne peut pas être différent de Science, Histoire, Geographie ou General et le nombre de questions doit être un nombre.")
        
        logging.info(f"User input - Quiz type: {quiz_type}, Number of questions: {num_questions}")
        return quiz_type, num_questions

    def generate_quiz_content(self, quiz_type: str, num_questions: str):
        """Generate quiz content and get user approval"""
        quiz_gen = QuizGenerator(self.config)
        quiz_content = quiz_gen.generate_quiz(quiz_type, num_questions)
        quiz_sections = quiz_gen.parse_quiz_content(quiz_content)
        
        print("\nContenu du quiz généré :")
        print(quiz_sections)
        
        return quiz_sections if self._get_user_approval() else None

    def _get_user_approval(self) -> bool:
        """Get user approval for the generated quiz"""
        while True:
            response = input("\nEst-ce que le quiz est bien ? (Oui/Non) : ").strip().lower()
            if response in ['oui', 'non']:
                return response == 'oui'
            print("Veuillez répondre par 'Oui' ou 'Non'")

    def save_quiz_content(self, quiz_sections) -> None:
        """Save quiz content to JSON file"""
        text_dir = self._create_subdirectory('text')
        json_file = text_dir / 'content.json'
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(asdict(quiz_sections), f, ensure_ascii=False, indent=4)
        logging.info(f"Saved quiz content to: {json_file}")

    def generate_media(self, quiz_sections) -> None:
        """Generate images and voices for the quiz"""
        # Generate images
        img_dir = self._create_subdirectory('images')
        image_gen = ImageGenerator(self.config, img_dir)
        image_paths = image_gen.generate_images(quiz_sections)
        logging.info("Generated images successfully")

        # Generate voices
        voice_dir = self._create_subdirectory('voices')
        voice_gen = VoiceGenerator(self.config, voice_dir)
        voice_gen.generate_all_voices(quiz_sections)
        logging.info("Generated voices successfully")

    def run(self):
        """Main application loop"""
        try:
            logging.info("Starting quiz generation process")
            
            # Get user input and generate content
            quiz_type, num_questions = self.get_user_input()
            quiz_sections = self.generate_quiz_content(quiz_type, num_questions)
 
            
            if quiz_sections is None:
                logging.info("Quiz generation cancelled by user")
                print("Génération du quiz annulée !")
                return
            
            # Generate all content
            self.save_quiz_content(quiz_sections)
            self.generate_media(quiz_sections)
            create_educational_video(
                images_dir="video_data/"+ self.date_str +"/images",
                audio_dir="video_data/"+ self.date_str +"/voices",
                output_file="video_data/"+ self.date_str +"/final_output.mp4",
                quiz_type=quiz_type
            )
            
            print("\nGénération du quiz terminée avec succès !")
            logging.info("Quiz generation completed successfully")

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}", exc_info=True)
            print(f"\nUne erreur est survenue : {str(e)}")
            print("Consultez le fichier de log pour plus de détails.")

def main():
    app = QuizApp()
    app.run()

if __name__ == "__main__":
    main()