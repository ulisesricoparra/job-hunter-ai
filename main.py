import os
from core.cv_parser import CVParser
from core.matcher import JobMatcher
from database.models import DatabaseManager
from scrapers.remoteok import RemoteOKScraper
from scrapers.getonboard import GetOnBoardScraper


def main():
    print("🚀 === INICIANDO JOB HUNTER AI (FASE 3) ===\n")

    # 1. Leer CV y extraer habilidades
    cv_file = "cv.pdf"  # Nombre de tu PDF de CV
    user_skills = []

    if os.path.exists(cv_file):
        parser = CVParser(cv_path=cv_file)
        cv_result = parser.parse()
        user_skills = cv_result["skills"]
        print(
            f"✅ CV cargado ({len(user_skills)} habilidades): {', '.join([s.capitalize() for s in user_skills[:8]])}...\n")
    else:
        print(f"⚠️ No se encontró '{cv_file}'. Usando lista de habilidades por defecto.")
        user_skills = ["python", "selenium", "pytest", "sql", "git", "postman", "jira"]

    # 2. Instanciar Motor de Matcher y BD
    matcher = JobMatcher(user_skills=user_skills)
    db = DatabaseManager(db_path="jobs.db")

    # 3. Ejecutar Scrapers
    scrapers = [RemoteOKScraper(), GetOnBoardScraper()]
    for scraper in scrapers:
        jobs = scraper.fetch_jobs()
        for job in jobs:
            db.save_job(job)

    # 4. Calcular compatibilidad de todas las vacantes en la BD
    all_jobs = db.get_all_jobs()
    print("\n⚡ Calculando porcentaje de compatibilidad para todas las vacantes...")

    for job in all_jobs:
        result = matcher.match(job.puesto, job.descripcion)
        db.update_job_compatibility(job.id, result["score"])

    # 5. Mostrar TOP 5 Vacantes con mayor compatibilidad
    print("\n🏆 === TOP VACANTES CON MAYOR COMPATIBILIDAD ===")

    # Volvemos a consultar ordenando por compatibilidad descendente
    sorted_jobs = sorted(db.get_all_jobs(), key=lambda x: x.compatibilidad, reverse=True)

    for idx, job in enumerate(sorted_jobs[:5], 1):
        match_info = matcher.match(job.puesto, job.descripcion)
        print(f"\n{idx}. [{job.compatibilidad}% Coincidencia] {job.empresa} - {job.puesto}")
        print(f"   Fuente: {job.fuente} | Modalidad: {job.modalidad}")
        print(f"   ✔ Coinciden ({len(match_info['matches'])}): {', '.join(match_info['matches'])}")
        if match_info['missing']:
            print(f"   ✖ Te faltan ({len(match_info['missing'])}): {', '.join(match_info['missing'])}")
        print(f"   🔗 URL: {job.url}")


if __name__ == "__main__":
    main()