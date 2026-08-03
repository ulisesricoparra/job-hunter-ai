import os
import time
import json
from typing import Dict, Any, List
from google import genai
from google.genai import types
from google.genai.errors import APIError


class AIJobAnalyzer:
    """Módulo de Inteligencia Artificial para análisis profundo y personalización de vacantes."""

    def __init__(self, api_key: str = None):
        # Utiliza la API Key de las variables de entorno si no se pasa explícitamente
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def analyze_job(self, job_title: str, company: str, description: str, user_skills: List[str]) -> Dict[str, Any]:
        """Genera un resumen ejecutivo y análisis de idoneidad con IA."""
        if not self.client:
            return {
                "resumen": "API Key de IA no configurada (GEMINI_API_KEY).",
                "requisitos_clave": [],
                "por_que_encajas": "Configura la API Key para habilitar el análisis avanzado de IA."
            }

        prompt = f"""
        Eres un reclutador senior especializado en QA Automation Engineer y desarrollo de software.
        Analiza la siguiente oferta laboral para un candidato con estas habilidades: {', '.join(user_skills)}.

        EMPRESA: {company}
        PUESTO: {job_title}
        DESCRIPCIÓN DE LA VACANTE:
        {description[:2500]}

        Por favor responde en formato JSON con la siguiente estructura estricta:
        {{
            "resumen": "Resumen ejecutivo de la oferta en máximo 2 oraciones.",
            "requisitos_clave": ["Requisito 1", "Requisito 2", "Requisito 3", "Requisito 4"],
            "por_que_encajas": "Explicación breve de por qué el perfil coincide o qué fortalezas destacan."
        }}
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            return json.loads(response.text)

        except APIError as e:
            # Si se excede la cuota/frecuencia (código 429), se espera 10 segundos y se reintenta
            if e.code == 429:
                print("Límite de peticiones alcanzado. Esperando 10 segundos antes de reintentar...")
                time.sleep(10)
                try:
                    response = self.client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.3
                        )
                    )
                    return json.loads(response.text)
                except Exception as retry_err:
                    print(f"Error tras el reintento: {retry_err}")
                    return {
                        "resumen": "Cuota de IA saturada momentáneamente.",
                        "requisitos_clave": [],
                        "por_que_encajas": "Por favor, reintenta dar clic en un momento."
                    }

            print(f"Error de API al llamar a la IA: {e}")
            return {
                "resumen": "Error durante el análisis con IA.",
                "requisitos_clave": [],
                "por_que_encajas": f"Detalle del error: {e.message if hasattr(e, 'message') else e}"
            }

        except Exception as e:
            print(f"Error inesperado al llamar a la API de IA: {e}")
            return {
                "resumen": "Error durante el análisis con IA.",
                "requisitos_clave": [],
                "por_que_encajas": f"Detalle del error: {e}"
            }

    def generate_cover_letter_draft(self, job_title: str, company: str, description: str,
                                    user_skills: List[str]) -> str:
        """Genera un borrador de carta de presentación o mensaje inicial para postulación."""
        if not self.client:
            return "Configura la variable GEMINI_API_KEY para generar borradores de carta de presentación."

        prompt = f"""
        Escribe un mensaje corto, profesional y convincente (máximo 150 palabras) en español (o inglés si la oferta está en inglés) para postular a la vacante de {job_title} en {company}.

        Mis habilidades principales son: {', '.join(user_skills)}.
        Descripción del empleo: {description[:1500]}

        Usa un tono directo, profesional y orientado a resultados de QA Automation Engineer.
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.5)
            )
            return response.text

        except APIError as e:
            if e.code == 429:
                print("Límite de peticiones alcanzado. Esperando 10 segundos antes de reintentar...")
                time.sleep(10)
                try:
                    response = self.client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(temperature=0.5)
                    )
                    return response.text
                except Exception as retry_err:
                    return f"Cuota de peticiones agotada. Por favor espera unos segundos y vuelve a intentar."
            return f"Error generando carta de presentación: {e.message if hasattr(e, 'message') else e}"

        except Exception as e:
            return f"Error generando carta de presentación: {e}"