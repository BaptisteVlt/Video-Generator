from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, concatenate_audioclips,vfx,  AudioClip, CompositeVideoClip,  CompositeAudioClip, afx, TextClip, ColorClip
import os
from PIL import Image
import math
import numpy as np
import random 
def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result

    return clip.transform(effect)

def zoom_out_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        initial_size = [
            math.ceil(img.size[0] * 0.70),
            math.ceil(img.size[1] * 0.70)
        ]

        current_size = [
            math.ceil(img.size[0] * (1 - (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 - (zoom_ratio * t)))
        ]

        # The new dimensions must be even.
        initial_size[0] = initial_size[0] + (initial_size[0] % 2)
        initial_size[1] = initial_size[1] + (initial_size[1] % 2)
        current_size[0] = current_size[0] + (current_size[0] % 2)
        current_size[1] = current_size[1] + (current_size[1] % 2)

        img = img.resize(current_size, Image.LANCZOS)

        x = math.ceil((current_size[0] - initial_size[0]) / 2)
        y = math.ceil((current_size[1] - initial_size[1]) / 2)

        img = img.crop([
            x, y, current_size[0] - x, current_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result

    return clip.transform(effect)

def left_to_right_smooth_travel_effect(clip, travel_ratio=0.02):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        # Calculate the horizontal travel distance
        travel_distance = math.ceil(base_size[0] * travel_ratio * t)

        # Ensure the crop stays within bounds
        left = min(travel_distance, base_size[0])
        right = min(left + base_size[0], base_size[0])

        # Crop and resize back to the original size
        img = img.crop([left, 0, right, base_size[1]])
        img = img.resize(base_size, Image.LANCZOS)

        result = np.array(img)
        img.close()

        return result

    return clip.transform(effect)


def create_educational_video(images_dir, audio_dir, output_file="output.mp4", quiz_type = 'histoire'):
    """
    Crée une vidéo éducative à partir d'images et fichiers audio.
    
    Args:
        images_dir (str): Chemin vers le dossier contenant les images
        audio_dir (str): Chemin vers le dossier contenant les fichiers audio
        output_file (str): Nom du fichier de sortie
    """
    
    # Liste pour stocker les clips
    clips = []
    fixed_size = (1920, 1080)

    # Ajout de l'introduction
    intro_audio = os.path.join(audio_dir, "Introduction.mp3")
    intro_image = os.path.join(
        "static_media", 
        "history.png" if quiz_type.lower() == "histoire" 
        else "geography.png" if quiz_type.lower() == "geographie" 
        else "science.png" if quiz_type.lower() == "science" 
        else "general_knowledge.png"
    )

    print("Ajout de l'introduction...")
    intro_audio_clip = AudioFileClip(intro_audio)
    intro_duration = intro_audio_clip.duration  # Obtenir la durée directement
    intro_clip = (ImageClip(intro_image)
                    .with_duration(intro_duration)
                    .with_audio(intro_audio_clip)) 
    clips.append(intro_clip)

    
    # Détermine le nombre de questions basé sur les fichiers présents
    question_files = sorted([f for f in os.listdir(images_dir) if f.startswith('q')])
    num_questions = len(question_files)
    
    for i in range(1, num_questions + 1):
        if i == num_questions:
            appel_abonnement_image = os.path.join("static_media", "general_knowledge.png")
            appel_abonnement_audio = os.path.join(audio_dir, "Appel.mp3")
            appel_abonnement_audio_clip = AudioFileClip(appel_abonnement_audio)
            appel_abonnement_duration = appel_abonnement_audio_clip.duration
            appel_clip = (ImageClip(appel_abonnement_image)
                        .with_duration(appel_abonnement_duration)
                        .with_audio(appel_abonnement_audio_clip))
            rd = random.randint(1, 3)
            if rd == 1:
                appel_clip = zoom_in_effect(appel_clip, 0.04)
            elif rd == 2:
                question_clip = zoom_out_effect(appel_clip, 0.04)
            else :
                question_clip = left_to_right_smooth_travel_effect(appel_clip, travel_ratio=0.02)
            clips.append(appel_clip)
        # Question
        question_image = os.path.join(images_dir, f"q{i}.png")
        question_audio = os.path.join(audio_dir, f"Question_{i}.mp3")
        
        
        # Charge l'audio de la question pour obtenir sa durée
        question_audio_clip = AudioFileClip(question_audio)
        question_duration = question_audio_clip.duration
        
        # Crée le clip de la question
        question_clip = (ImageClip(question_image)
                        .with_duration(question_duration)
                        .with_audio(question_audio_clip))
        
        rd = random.randint(1, 3)

        if rd == 1:
            question_clip = zoom_in_effect(question_clip, 0.04)
        elif rd == 2:
            question_clip = zoom_out_effect(question_clip, 0.04)
        else :
            question_clip = left_to_right_smooth_travel_effect(question_clip, travel_ratio=0.02)
        clips.append(question_clip)
        
        # Ajoute une pause de 4 secondes (image de la question sans son)
        pause_audio_clip = (AudioFileClip(os.path.join("static_media", "chronometre.mp3")).subclipped(0, 4))
        pause_clip = (ImageClip(question_image)
                      .with_duration(3)
                      .with_audio(pause_audio_clip))
        clips.append(pause_clip)
        
        # Réponse
        answer_image = os.path.join(images_dir, f"r{i}.png")
        answer_audio = os.path.join(audio_dir, f"Reponse_{i}.mp3")
        
        # Charge l'audio de la réponse pour obtenir sa durée
        answer_audio_clip = AudioFileClip(answer_audio)
        answer_duration = answer_audio_clip.duration
        
        # Crée le clip de la réponse
        answer_clip = (ImageClip(answer_image)
                      .with_duration(answer_duration)
                      .with_audio(answer_audio_clip))
        
        rd = random.randint(1, 2)
        if rd == 1:
            answer_clip = zoom_in_effect(answer_clip, 0.04)
        elif rd == 2 :
            answer_clip = zoom_out_effect(answer_clip, 0.04)
        else :
            question_clip = left_to_right_smooth_travel_effect(question_clip, travel_ratio=0.02)
        clips.append(answer_clip)
    
    # Assemble tous les clips
    final_clip = concatenate_videoclips(clips)
    
    # Exporte la vidéo
    final_clip.write_videofile(output_file, 
                             fps=24, 
                             audio_codec='aac',
                             audio_bitrate='192k')
    
    # Nettoie la mémoire
    final_clip.close()
    for clip in clips:
        clip.close()

# # Exemple d'utilisation
# if __name__ == "__main__":
#     create_educational_video(
#         images_dir="video_data/01-18-25/images",
#         audio_dir="video_data/01-18-25/voices",
#         output_file="video_data/01-18-25/final_output.mp4",
#         quiz_type='histoire'
#     )