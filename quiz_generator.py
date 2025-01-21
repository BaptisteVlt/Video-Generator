from openai import OpenAI
from typing import Dict
import re
from models import QuizSection
from config import Config
import json

class QuizGenerator:
    def __init__(self, config: Config):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.instruction = """
        Tu es un expert en création de contenu viral pour TikTok, spécialisé dans les quiz éducatifs et divertissants.

        Génère un quiz de culture générale adapté au format TikTok avec ces caractéristiques :
        - Il faut être le plus clair possible
        - Ton informel et dynamique, utilisant le "tu" et des expressions jeunes
        - Réponses courtes et mémorables, incluant un fait additionnel intéressant
        - Thématique cohérente pour l'ensemble des questions
        - Chaque question doit être visuellement imaginable
        - Éviter les questions abstraites ou purement textuelles
        - L'appel à l'abonnement sera toujours avant la dernière question

        Format de sortie JSON :
        {
            "introduction": "courte phrase d'accroche",
            "questions": {
                "question_1": "question surprenante",
                "question_2": "question surprenante"
            },
            "reponses": {
                "reponse_1": "réponse + fait intéressant",
                "reponse_2": "réponse + fait intéressant"
            },
            "appel_abonnement": "call-to-action dynamique",
            "mots_clefs": ["mots clés précis pour la génération d'image"],
            "prompts_image": {
                "prompt_1": "description détaillée pour l'image de la question 1",
                "prompt_2": "description détaillée pour l'image de la question 2"
            }
        }


        """
        self.examples = """
{
    "exemple_1": {
        "input": {
            "type_quiz": "science",
            "nombre_questions": 6,
            "langue": "français"
        },
        "output": {
            "introduction": "Est-ce que tu pourrais être bac en sciences. Je vais te poser six questions qui vont du niveau collège au niveau bac et on va voir où tu te situes.",
            "questions": {
                "question_1": "Question numéro une de niveau collège, quelle est la planète la plus proche du soleil ?",
                "question_2": "Numéro deux, quel est le symbole chimique de l'eau ?",
                "question_3": "Numéro trois dans le tableau périodique quel élément correspond au symbole f e.",
                "question_4": "Numéro quatre, on passe au niveau lycée, vrai ou faux, c'est Niels Bohr qui a découvert les lois de la gravitation universelle ?",
                "question_5": "Numéro cinq, quel est le nom de la théorie qui explique l'origine de l'univers ?",
                "question_6": "Numéro 6, quelle unité mesure l'intensité d'un courant électrique ?"
            },
            "reponses": {
                "reponse_1": "Oui c'est Mercure.",
                "reponse_2": "C'est bien H2O",
                "reponse_3": "C'est le fer.",
                "reponse_4": "Bien c'est faux puisque c'est Newton.",
                "reponse_5": "C'est le big bang.",
                "reponse_6": "Il s'agit de l'ampère."
            },
            "appel_abonnement": "Avant de passer à la question suivante n'oublie pas de t'abonner, et dis moi en commentaire quel est ton score final !",
            "mots_clefs": ["Science", "planète", "Mercure", "Eau", "H2O", "Tableau périodique", "Fer", "Gravitation", "Isaac Newton", "Univers", "Big bang", "Electrique", "Ampère"],
            "prompts_image_questions": {
                "prompt_q1": "An artistic illustration of the solar system seen from above, showing the Sun at the center and a small planet orbiting closest to it, but the planet's identity should not be explicitly shown.",
                "prompt_q2": "A glass of water on a laboratory table, surrounded by scientific equipment like test tubes and beakers, with a hint of mystery regarding its chemical composition.",
                "prompt_q3": "A periodic table of elements with certain symbols highlighted but no specific element identified, creating curiosity about which one corresponds to 'Fe'.",
                "prompt_q4": "A split image showing Niels Bohr and Isaac Newton, each surrounded by scientific symbols like equations and diagrams, leaving it ambiguous who is associated with which discovery.",
                "prompt_q5": "A cosmic scene showing a mysterious and colorful explosion in the universe, with galaxies and stars forming, hinting at the origin of the cosmos without explicitly naming it.",
                "prompt_q6": "A physics classroom or a scientific laboratory setting, with electrical circuits and measuring devices like ammeters and voltmeters, leaving the specific unit unidentified."
            },
            "prompts_image_reponses": {
                "prompt_r1": "A detailed depiction of Mercury, the smallest planet in the solar system, with its gray, cratered surface, and the Sun appearing large and bright in the background.",
                "prompt_r2": "An artistic representation of the molecular structure of water, with two hydrogen atoms bonded to a single oxygen atom, depicted in a colorful and dynamic style.",
                "prompt_r3": "A close-up view of an iron bar, rusty and textured, with the chemical symbol 'Fe' subtly engraved or glowing on its surface.",
                "prompt_r4": "A classic illustration of Isaac Newton under the apple tree, with the concept of gravity represented by mathematical symbols and falling apples.",
                "prompt_r5": "An artistic depiction of the Big Bang, with a bright explosion at the center radiating energy, matter, and light into the dark void of space.",
                "prompt_r6": "A close-up of an ammeter in use, its needle pointing to a specific value, with the word 'Ampere' clearly visible on the device."
            }
        }
    },
    "exemple_2": {
        "input": {
            "type_quiz": "géographie",
            "nombre_questions": 6,
            "langue": "français"
        },
        "output": {
            "introduction": "Est-ce que tu te considères au-dessus de la moyenne en géographie Réponds à ces dix questions et si tu as moins de cinq sur dix, tu es une merguez.",
            "questions": {
                "question_1": "Première question : quel pays a récemment quitté l'Union Européenne ?",
                "question_2": "Numéro deux, quelle est la capitale du Portugal ?",
                "question_3": "Numéro trois, quel est le fleuve le plus long d'Afrique Est-ce que c'est le Nil, le Congo ou le Zambèze ?",
                "question_4": "On passe au niveau moyen dans quel océan se trouve l'île de Madagascar ?",
                "question_5": "Numéro 5, quel est le pays le moins peuplé du monde ?",
                "question_6": "Dernière question ! quel pays est bordé par la mer rouge et par l'océan Indien"
            },
            "reponses": {
                "reponse_1": "C'est l'Angleterre ! Les anglais ont quitté l'Union Européenne lors du Brexit !",
                "reponse_2": "Biensûr c'est Lisbonne !",
                "reponse_3": "Oui, c'est bien évidemment le Nil.",
                "reponse_4": "Bien c'est dans l'océan indien",
                "reponse_5": "Il s'agit du Vatican.",
                "reponse_6": "C'est le Yémen"
            },
            "appel_abonnement": "Avant la dernière question, si tu ne veux pas rester aussi nul qu'un Américain en Géographie, abonne toi !",
            "mots_clefs": ["Geographie", "union européenne", "Angleterre", "Portugal", "Lisbonne", "Fleuve", "Nil", "Madagascar", "Ocean Indien", "Pays", "Vatican", "Indien"],
            "prompts_image_questions": {
                "prompt_q1": "A European map with a specific country highlighted in gray, surrounded by the EU flag with question marks, leaving the country's identity ambiguous.",
                "prompt_q2": "A colorful map of Portugal with a question mark positioned near its center, focusing on the mystery of its capital city.",
                "prompt_q3": "A serene African river landscape with three rivers labeled 'A,' 'B,' and 'C,' each representing the Nile, Congo, and Zambezi, without revealing which is which.",
                "prompt_q4": "A world map focusing on the Indian Ocean region, with Madagascar highlighted and surrounded by marine life, emphasizing its oceanic location.",
                "prompt_q5": "A minimalist globe with a small dot marking a location and a large question mark hovering nearby, symbolizing the search for the least populated country.",
                "prompt_q6": "A geographical map showing the Red Sea and the Indian Ocean, with question marks over a nearby country, leaving its identity unrevealed."
            },
            "prompts_image_reponses": {
                "prompt_r1": "An illustration of the United Kingdom with the Union Jack flag and a symbolic depiction of the Brexit referendum, showing the country separating from the EU.",
                "prompt_r2": "A vibrant cityscape of Lisbon, featuring iconic landmarks like the Belém Tower and colorful streets, with a bright and lively atmosphere.",
                "prompt_r3": "A majestic view of the Nile River, showing a wide expanse of water surrounded by lush greenery and ancient Egyptian monuments.",
                "prompt_r4": "A scenic depiction of Madagascar, with its unique fauna like lemurs and baobab trees, and the Indian Ocean in the background.",
                "prompt_r5": "A detailed illustration of Vatican City, featuring St. Peter's Basilica and its surrounding architecture, with a small, peaceful ambiance.",
                "prompt_r6": "A depiction of Yemen's coastal region, with the Red Sea on one side and the Indian Ocean on the other, showcasing its geographic location with cultural elements."
            }
        }
    }
}
"""


    def generate_quiz(self, quiz_type: str, num_questions: int) -> str:
        input_user = self.examples + f"""
        Input:
        type de quizz : {quiz_type}
        nombre de questions : {num_questions}
        output:
        """

        completion = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "developer", "content": self.instruction},
                {"role": "user", "content": input_user}
            ]
        )
        return completion.choices[0].message.content

    def parse_quiz_content(self, text: str) -> QuizSection:
        try:
            # Parse the JSON content directly
            content = json.loads(text)
            
            return QuizSection(
                introduction=content.get('introduction', ''),
                questions=content.get('questions', {}),
                reponses=content.get('reponses', {}),
                appel_abonnement=content.get('appel_abonnement', ''),
                mots_clefs=content.get('mots_clefs', []),
                prompts_image_questions=content.get('prompts_image_questions', {}),
                prompts_image_reponses=content.get('prompts_image_reponses', {})
            )
        except json.JSONDecodeError:
            # Fallback to regex parsing if content is not valid JSON
            intro_match = re.search(r"Introduction : (.+?)(?=\n)", text, re.DOTALL)
            introduction = intro_match.group(1).strip() if intro_match else ""

            questions = {}
            for match in re.finditer(r"Question_(\d+) : (.+?)(?=\n)", text):
                questions[f"question_{match.group(1)}"] = match.group(2).strip()

            reponses = {}
            for match in re.finditer(r"Réponse_(\d+) : (.+?)(?=\n)", text):
                reponses[f"reponse_{match.group(1)}"] = match.group(2).strip()

            appel_match = re.search(r"Appel_abonnement : (.+?)(?=\n)", text)
            appel_abonnement = appel_match.group(1).strip() if appel_match else ""

            mots_clefs_match = re.search(r"Mots_clefs : (.+?)(?=\n|$)", text)
            mots_clefs = [mot.strip() for mot in mots_clefs_match.group(1).split(',')] if mots_clefs_match else []

            # Default empty dict for prompts_image in legacy format
            prompts_image_questions = {}
            prompts_image_reponses = {}

            return QuizSection(
                introduction=introduction,
                questions=questions,
                reponses=reponses,
                appel_abonnement=appel_abonnement,
                mots_clefs=mots_clefs,
                prompts_image_questions=prompts_image_questions,
                prompts_image_reponses=prompts_image_reponses
            )
