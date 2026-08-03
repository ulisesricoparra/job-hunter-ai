import os
from core.cv_parser import CVParser
from database.models import DatabaseManager


def main():
    print("🚀 Probando Fase 1 (CV) y Fase 2 (SQLite Database)...\n")

    # 1. Probar CV Parser
    cv_file = "cv.pdf"  # Asegúrate de que coincida con tu archivo PDF
    if os.path.exists(cv_file):
        parser = CVParser(cv_path=cv_file)
        cv_result = parser.parse()
        print(f"✅ CV procesado: {len(cv_result['skills'])} habilidades detectadas.")
    else:
        print(f"⚠️  No se encontró {cv_file}, continuando prueba con DB...")

    # 2. Probar Base de Datos
    db = DatabaseManager(db_path="jobs.db")

    # Vacante de ejemplo
    sample_job = {
        "empresa": "Oracle",
        "puesto": "QA Automation Engineer",
        "salario": "$3,500 - $4,500 USD",
        "modalidad": "Remote",
        "ubicacion": "Mexico",
        "descripcion": "Buscamos QA Engineer con experiencia en Python, Pytest, Selenium, SQL y Git.",
        "url": "https://example.com/jobs/qa-automation-oracle-1",
        "fuente": "GetOnBoard",
        "fecha_publicacion": "2026-08-02"
    }

    inserted = db.save_job(sample_job)
    if inserted:
        print("✅ Vacante de prueba insertada correctamente en SQLite!")
    else:
        print("ℹ️  La vacante ya existía en la base de datos (control de duplicados OK).")

    all_jobs = db.get_all_jobs()
    print(f"📊 Total de vacantes almacenadas en BD: {len(all_jobs)}")
    for j in all_jobs:
        print(f"   • [{j.fuente}] {j.empresa} - {j.puesto} ({j.modalidad})")


if __name__ == "__main__":
    main()