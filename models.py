from dataclasses import dataclass
from typing import List, Dict

@dataclass
class QuizSection:
    introduction: str
    questions: dict
    reponses: dict
    appel_abonnement: str
    mots_clefs: List[str]
    prompts_image_questions: dict
    prompts_image_reponses: dict
