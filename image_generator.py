from openai import OpenAI
from typing import Dict, List, Optional
from models import QuizSection
from config import Config
import base64
import requests
from pathlib import Path
import os

class ImageGenerator:
    def __init__(self, config: Config, OUTPUT_IMAGE_DIR: str):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.output_dir = OUTPUT_IMAGE_DIR
        os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)

    def generate_images(self, quiz_section: QuizSection) -> Dict[str, Dict[str, str]]:
        """
        Generate both question and answer images for the quiz using the respective prompts
        
        Returns:
            Dict with two keys: 'questions' and 'answers', each containing a dictionary
            mapping question numbers to image file paths
        """
        image_paths = {
            'questions': {},
            'answers': {}
        }
        
        # Generate question images
        for question_num, prompt in quiz_section.prompts_image_questions.items():
            try:
                # Extract question number (e.g., "q1" from "prompt_q1")
                num = question_num.split('_')[1]
                
                # Enhance the prompt for better image generation
                enhanced_prompt = self._enhance_prompt(prompt)
                
                # Generate image using DALL-E
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1792",  # TikTok format
                    quality="standard",
                    n=1
                )

                # Get the image URL
                image_url = response.data[0].url

                # Download and save the image with "q" prefix
                image_path = self._download_and_save_image(
                    image_url, 
                    f"{num}.png"
                )
                
                image_paths['questions'][question_num] = str(image_path)
                
            except Exception as e:
                print(f"Error generating question image for {question_num}: {str(e)}")
                continue

        # Generate answer images
        for answer_num, prompt in quiz_section.prompts_image_reponses.items():
            try:
                # Extract answer number (e.g., "r1" from "prompt_r1")
                num = answer_num.split('_')[1]
                
                # Enhance the prompt for better image generation
                enhanced_prompt = self._enhance_prompt(prompt)
                
                # Generate image using DALL-E
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=enhanced_prompt,
                    size="1024x1792",  # TikTok format
                    quality="standard",
                    n=1
                )

                # Get the image URL
                image_url = response.data[0].url

                # Download and save the image with "a" prefix
                image_path = self._download_and_save_image(
                    image_url, 
                    f"{num}.png"
                )
                
                image_paths['answers'][answer_num] = str(image_path)
                
            except Exception as e:
                print(f"Error generating answer image for {answer_num}: {str(e)}")
                continue
                
        return image_paths

    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance the image prompt with additional parameters for better quality
        """
        enhancement = (
            "No text in the image"
            "The style should be vibrant and engaging, with good lighting and composition."
            "Try to use pastel color"
        )
        
        return enhancement + prompt

    def _download_and_save_image(self, image_url: str, filename: str) -> str:
        """
        Download image from URL and save it to the output directory
        """
        response = requests.get(image_url)
        response.raise_for_status()
        
        file_path = os.path.join(self.output_dir, filename)
        with open(file_path, "wb") as f:
            f.write(response.content)
            
        return file_path
