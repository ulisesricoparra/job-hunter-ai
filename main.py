import os
from core.cv_parser import CVParser
from database.models import DatabaseManager
from scrapers.remoteok import RemoteOKScraper
from scrapers.getonboard import GetOnBoardScraper


def main():
    print("🚀 === INICIANDO JOB HUNTER AI ===\n")

    # 1. Instanciar gestor de base de datos
    db = DatabaseManager(db_path="jobs.db")

    # 2. Correr Scrapers
    scrapers = [
        RemoteOKScraper(),
        GetOnBoardScraper()
    ]

    new_jobs_count = 0
    total_fetched = 0

    for scraper in scrapers:
        jobs = scraper.fetch_jobs()
        total_fetched += len(jobs)
        for job in jobs:
            if db.save_job(job):
                new_jobs_count += 1

    print("\n📊 === RESUMEN DE EXTRACCIÓN ===")
    print(f"• Vacantes consultadas en la red: {total_fetched}")
    print(f"• Nuevas vacantes guardadas en BD: {new_jobs_count}")

    all_jobs_in_db = db.get_all_jobs()
    print(f"• Total histórico acumulado en BD: {len(all_jobs_in_db)}")

    print("\n📄 Últimas 5 vacantes registradas:")
    for j in all_jobs_in_db[-5:]:
        print(f"   [{j.fuente}] {j.empresa} -> {j.puesto} ({j.modalidad})")


if __name__ == "__main__":
    main()