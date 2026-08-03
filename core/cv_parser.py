import os
import re
from typing import List, Set, Dict, Any
from pypdf import PdfReader

# Lista base de habilidades de QA, Backend, DB y DevOps a rastrear
DEFAULT_SKILLS_KEYWORDS = [
    # QA & Test Automation
    "selenium", "pytest", "playwright", "cypress", "appium", "postman", "jmeter",
    "rest assured", "cucumber", "qa", "automation engineer", "manual testing",
    "api testing", "regression testing", "test plans", "test cases", "jira", "zephyr",

    # Backend & Programming
    "python", "java", "javascript", "typescript", "fastapi", "django", "flask",
    "node.js", "express", "sql", "postgresql", "mysql", "mongodb",

    # Tools, DevOps & Methodology
    "git", "github", "gitlab", "docker", "kubernetes", "ci/cd", "github actions",
    "jenkins", "aws", "azure", "scrum", "agile", "kanban", "linux", "bash"
]


class CVParser:
    """Clase encargada de extraer texto de un CV en PDF y parsear sus habilidades."""

    def __init__(self, cv_path: str, custom_skills: List[str] = None):
        """
        :param cv_path: Ruta relativa o absoluta del archivo PDF del CV.
        :param custom_skills: Lista opcional de habilidades adicionales a buscar.
        """
        self.cv_path = cv_path
        self.skills_to_search = set(
            [skill.lower() for skill in (custom_skills or DEFAULT_SKILLS_KEYWORDS)]
        )

    def extract_text_from_pdf(self) -> str:
        """Lee el contenido del archivo PDF y devuelve todo el texto extraído."""
        if not os.path.exists(self.cv_path):
            raise FileNotFoundError(f"No se encontró el archivo del CV en: {self.cv_path}")

        reader = PdfReader(self.cv_path)
        extracted_text = []

        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        return "\n".join(extracted_text)

    def extract_skills(self, text: str) -> List[str]:
        """
        Busca las habilidades clave dentro del texto normalizado usando límites de palabras (regex).
        """
        text_lower = text.lower()
        found_skills: Set[str] = set()

        for skill in self.skills_to_search:
            # Escapar caracteres especiales para regex (por ejemplo: 'c++', 'ci/cd', 'node.js')
            pattern = r'(?:\b|_)' + re.escape(skill) + r'(?:\b|_)'
            if re.search(pattern, text_lower):
                found_skills.add(skill)

        return sorted(list(found_skills))

    def parse(self) -> Dict[str, Any]:
        """Ejecuta la lectura completa del CV y retorna el resumen estructurado."""
        raw_text = self.extract_text_from_pdf()
        detected_skills = self.extract_skills(raw_text)

        return {
            "cv_path": self.cv_path,
            "raw_text_length": len(raw_text),
            "skills": detected_skills
        }