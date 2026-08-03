import requests
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper


class RemoteOKScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="RemoteOK")
        self.url = "https://remoteok.com/api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) QA-Job-Hunter/1.0"
        }

    def fetch_jobs(self) -> List[Dict[str, Any]]:
        print(f"🔍 [{self.name}] Consultando ofertas de empleo...")
        jobs = []
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()

                # El primer elemento de RemoteOK API suele ser metadatos legales
                raw_jobs = [item for item in data if isinstance(item, dict) and "position" in item]

                for item in raw_jobs[:15]:  # Tomamos las primeras 15 ofertas más recientes
                    tags = ", ".join(item.get("tags", []))
                    description = f"Tags: {tags}\n\n{item.get('description', '')}"

                    job = {
                        "empresa": item.get("company", "Desconocida"),
                        "puesto": item.get("position", "Sin título"),
                        "salario": f"${item.get('salary_min', 0)} - ${item.get('salary_max', 0)} USD" if item.get(
                            'salary_min') else "No especificado",
                        "modalidad": "Remote",
                        "ubicacion": item.get("location", "Worldwide"),
                        "descripcion": description,
                        "url": item.get("url", item.get("apply_url", "")),
                        "fuente": self.name,
                        "fecha_publicacion": item.get("date", "")[:10]
                    }
                    jobs.append(job)
                print(f"✅ [{self.name}] Se obtuvieron {len(jobs)} vacantes.")
            else:
                print(f"⚠️  [{self.name}] Error en la respuesta HTTP: {response.status_code}")
        except Exception as e:
            print(f"❌ [{self.name}] Error al conectar con la API: {e}")

        return jobs