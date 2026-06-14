import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "Studify"
MAIN_FILE = "tabs_app.py"

PROJECT_DIR = Path(__file__).resolve().parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
SPEC_FILE = PROJECT_DIR / f"{APP_NAME}.spec"

ICON_FILE = PROJECT_DIR / "img" / "logo.ico"

DATA_FILES = [
    "studio.json",
    "schedule.json",
    "exams.json",
    "theme_pref.json",
]

DATA_DIRS = [
    "img",
]


def check_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller non è installato.")
        print("Installa con:")
        print("python -m pip install pyinstaller")
        sys.exit(1)


def clean_old_build():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    if SPEC_FILE.exists():
        SPEC_FILE.unlink()


def add_data(source: Path, destination: str) -> str:
    separator = ";" if os.name == "nt" else ":"
    return f"{source}{separator}{destination}"


def build_command() -> list[str]:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
    ]

    if ICON_FILE.exists():
        print(f"Uso icona exe: {ICON_FILE}")
        command.append(f"--icon={ICON_FILE}")
    else:
        print(f"ATTENZIONE: icona non trovata: {ICON_FILE}")

    for file_name in DATA_FILES:
        file_path = PROJECT_DIR / file_name

        if file_path.exists():
            command.extend(["--add-data", add_data(file_path, ".")])

    for dir_name in DATA_DIRS:
        dir_path = PROJECT_DIR / dir_name

        if dir_path.exists():
            command.extend(["--add-data", add_data(dir_path, dir_name)])

    command.append(str(PROJECT_DIR / MAIN_FILE))
    return command


def copy_editable_files():
    app_folder = DIST_DIR / APP_NAME

    if not app_folder.exists():
        return

    for file_name in DATA_FILES:
        source = PROJECT_DIR / file_name
        destination = app_folder / file_name

        if source.exists():
            shutil.copy2(source, destination)

    source_img = PROJECT_DIR / "img"
    destination_img = app_folder / "img"

    if source_img.exists():
        if destination_img.exists():
            shutil.rmtree(destination_img)

        shutil.copytree(source_img, destination_img)


def main():
    print("Creo l'eseguibile di Studify...")

    check_pyinstaller()
    clean_old_build()

    command = build_command()
    subprocess.run(command, check=True)

    copy_editable_files()

    print()
    print("Build completata.")
    print(f"Cartella app: {DIST_DIR / APP_NAME}")
    print(f"Eseguibile: {DIST_DIR / APP_NAME / (APP_NAME + '.exe')}")


if __name__ == "__main__":
    main()