import requests
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper


class GetOnBoardScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="GetOnBoard")
        # Búsqueda enfocado en vacantes de QA y Testing
        self.url = "https://www.getonbrd.com/api/v0/categories/programming/jobs?per_page=15&page=1"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QA-Job-Hunter/1.0"
        }

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        print(f"🔍 [{self.name}] Consultando ofertas de empleo...")
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get("data", [])

                for item in data:
                    attrs = item.get("attributes", {})
                    company_data = attrs.get("company", {}).get("data", {}).get("attributes", {})

                    job = {
                        "empresa": company_data.get("name", "Desconocida"),
                        "puesto": attrs.get("title", "Sin título"),
                        "salario": "No especificado",
                        "modalidad": "Remote" if attrs.get("remote") else "Presencial/Híbrido",
                        "ubicacion": attrs.get("country", "Latam/Remote"),
                        "descripcion": attrs.get("description", "Sin descripción"),
                        "url": attrs.get("projects_url", attrs.get("perks", "")),
                        "fuente": self.name,
                        "fecha_publicacion": str(attrs.get("published_at", ""))[:10]
                    }
                    jobs.append(job)
                print(f"✅ [{self.name}] Se obtuvieron {len(jobs)} vacantes.")
            else:
                print(f"⚠️  [{self.name}] Error en la respuesta HTTP: {response.status_code}")
        except Exception as e:
            print(f"❌ [{self.name}] Error al conectar con la API: {e}")

        return jobs