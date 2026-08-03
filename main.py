import os
from core.cv_parser import CVParser


def main():
    print("🚀 Probando el módulo CVParser...\n")

    # Reemplaza 'tu_cv.pdf' por el nombre exacto de tu archivo PDF en la raíz
    cv_file = "cv.pdf"

    if not os.path.exists(cv_file):
        print(
            f"⚠️  Atención: Por favor coloca tu archivo PDF en la raíz y actualiza el nombre en main.py (Buscado: '{cv_file}')")
        return

    parser = CVParser(cv_path=cv_file)
    result = parser.parse()

    print("✅ Extracción exitosa del CV!")
    print(f"📄 Caracteres leídos: {result['raw_text_length']}")
    print(f"🛠️  Habilidades detectadas ({len(result['skills'])}):")
    for skill in result['skills']:
        print(f"   • {skill.capitalize()}")


if __name__ == "__main__":
    main()