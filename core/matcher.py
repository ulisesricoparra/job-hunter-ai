import re
from typing import List, Dict, Set, Any
from core.cv_parser import DEFAULT_SKILLS_KEYWORDS

class JobMatcher:
    """Clase para comparar las habilidades del CV con la descripción de una vacante."""

    def __init__(self, user_skills: List[str]):
        """
        :param user_skills: Lista de habilidades detectadas en el CV del usuario.
        """
        self.user_skills = set([s.lower() for s in user_skills])
        # Diccionario general de habilidades conocidas para buscar en la oferta
        self.all_known_skills = set([s.lower() for s in DEFAULT_SKILLS_KEYWORDS])

    def extract_required_skills(self, text: str) -> Set[str]:
        """Extrae todas las habilidades requeridas presentes en el texto de la vacante."""
        text_lower = text.lower()
        required_skills: Set[str] = set()

        for skill in self.all_known_skills:
            pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
            if re.search(pattern, text_lower):
                required_skills.add(skill)

        return required_skills

    def match(self, job_title: str, job_description: str) -> Dict[str, Any]:
        """
        Calcula la puntuación de compatibilidad entre el CV y la vacante.
        """
        full_text = f"{job_title} {job_description}"
        required_skills = self.extract_required_skills(full_text)

        if not required_skills:
            # Si la oferta no menciona explícitamente tecnologías de nuestra lista base
            return {
                "score": 50.0,
                "matches": [],
                "missing": [],
                "total_required": 0
            }

        # Coincidencias entre las habilidades requeridas por la empresa y las del usuario
        matches = list(required_skills.intersection(self.user_skills))
        missing = list(required_skills.difference(self.user_skills))

        # Cálculo de porcentaje
        score = (len(matches) / len(required_skills)) * 100.0

        return {
            "score": round(score, 1),
            "matches": sorted(matches),
            "missing": sorted(missing),
            "total_required": len(required_skills)
        }