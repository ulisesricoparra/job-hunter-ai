from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScraper(ABC):
    """Clase base abstracta para todos los scrapers de ofertas laborales."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_jobs(self) -> List[Dict[str, Any]]:
        """
        Método obligatorio que debe implementar cada scraper.
        Debe devolver una lista de diccionarios con la estructura estándar:
        {
            "empresa": str,
            "puesto": str,
            "salario": str,
            "modalidad": str,
            "ubicacion": str,
            "descripcion": str,
            "url": str,
            "fuente": str,
            "fecha_publicacion": str
        }
        """
        pass