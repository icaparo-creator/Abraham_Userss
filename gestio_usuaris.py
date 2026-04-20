#!/usr/bin/env python3
"""
gestio_usuaris.py
-----------------
Lee el Google Sheet "Usuaris_Abraham" y:
  - Columna A (NOUS_USUARIS)     → crea los usuarios en el sistema
  - Columna B (USUARIS_ELIMINAR) → elimina los usuarios del sistema

Una vez procesados, vacía las celdas del sheet automáticamente.

Requisitos:
    pip install google-api-python-client google-auth

Uso:
    sudo python3 gestio_usuaris.py        (Linux)
    python gestio_usuaris.py              (Windows, PowerShell como Administrador)
"""

import os
import sys
import platform
import subprocess

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# ─────────────────────────────────────────────
# CONFIGURACIÓN — edita estos valores si es necesario
# ─────────────────────────────────────────────
SPREADSHEET_ID   = "1aSTUlXtgvPiMsJF9TEB7m-ZQ1IqfAekjQcVwDpn2IA8"
SHEET_RANGE      = "Full 1!A2:B1000"
CREDENTIALS_FILE = "credentials.json"
# ─────────────────────────────────────────────

# Necesitamos permiso de escritura para poder vaciar el sheet
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

IS_WINDOWS = platform.system() == "Windows"


# ── Google Sheets ─────────────────────────────

def get_service():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def get_sheet_data(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_RANGE
    ).execute()

    rows = result.get("values", [])
    nuevos   = []
    eliminar = []

    for row in rows:
        col_a = row[0].strip() if len(row) > 0 and row[0].strip() else None
        col_b = row[1].strip() if len(row) > 1 and row[1].strip() else None
        if col_a:
            nuevos.append(col_a)
        if col_b:
            eliminar.append(col_b)

    return nuevos, eliminar


def clear_sheet(service):
    """Vacia el sheet usando el numero de filas real del sheet."""
    # Obtener metadata para saber cuantas filas tiene la hoja
    meta = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID,
        fields="sheets.properties"
    ).execute()
    sheet_props = meta["sheets"][0]["properties"]["gridProperties"]
    row_count = sheet_props["rowCount"]

    # Sobreescribir TODAS las filas (excepto cabecera) con valores vacios
    full_range = f"Full 1!A2:B{row_count}"
    empty_rows = [["", ""] for _ in range(row_count - 1)]
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=full_range,
        valueInputOption="RAW",
        body={"values": empty_rows}
    ).execute()
    # Clear final
    service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range=full_range
    ).execute()
    print("\n\u2714 Sheet vaciado correctamente.")


# ── Funciones Linux ───────────────────────────

def user_exists_linux(username):
    return subprocess.run(["id", username], capture_output=True).returncode == 0

def create_user_linux(username):
    if user_exists_linux(username):
        print(f"  [!] '{username}' ya existe. Se omite.")
        return
    result = subprocess.run(["useradd", "-m", "-s", "/bin/bash", username], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [ERROR] No se pudo crear '{username}': {result.stderr.strip()}")
        return
    # Asignar contraseña
    passwd = subprocess.run(["chpasswd"], input=f"{username}:P@ssw0rd", capture_output=True, text=True)
    if passwd.returncode == 0:
        print(f"  [+] Usuario '{username}' creado con contraseña.")
    else:
        print(f"  [ERROR] Usuario creado pero no se pudo asignar contraseña: {passwd.stderr.strip()}")

def delete_user_linux(username):
    if not user_exists_linux(username):
        print(f"  [!] '{username}' no existe. Se omite.")
        return
    result = subprocess.run(["userdel", "-r", username], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [-] Usuario '{username}' eliminado.")
    else:
        print(f"  [ERROR] No se pudo eliminar '{username}': {result.stderr.strip()}")


# ── Funciones Windows ─────────────────────────

def user_exists_windows(username):
    return subprocess.run(["net", "user", username], capture_output=True).returncode == 0

def create_user_windows(username):
    if user_exists_windows(username):
        print(f"  [!] '{username}' ya existe. Se omite.")
        return
    # Crear usuario con contraseña, como usuario normal (sin /add al grupo Administradores)
    result = subprocess.run(
        ["net", "user", username, "P@ssw0rd", "/add", "/comment:Usuario estándar"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"  [+] Usuario '{username}' creado con contraseña.")
    else:
        print(f"  [ERROR] No se pudo crear '{username}': {result.stderr.strip()}")

def delete_user_windows(username):
    if not user_exists_windows(username):
        print(f"  [!] '{username}' no existe. Se omite.")
        return
    result = subprocess.run(["net", "user", username, "/delete"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [-] Usuario '{username}' eliminado.")
    else:
        print(f"  [ERROR] No se pudo eliminar '{username}': {result.stderr.strip()}")


# ── Main ──────────────────────────────────────

def check_admin():
    if IS_WINDOWS:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("[ERROR] Ejecuta el script como Administrador.")
            sys.exit(1)
    else:
        if os.geteuid() != 0:
            print("[ERROR] Ejecuta el script con sudo o como root.")
            sys.exit(1)


def main():
    check_admin()

    print("Conectando con Google Sheets...")
    try:
        service = get_service()
        nuevos, eliminar = get_sheet_data(service)
    except FileNotFoundError:
        print(f"[ERROR] No se encontró '{CREDENTIALS_FILE}'. Colócalo junto al script.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] No se pudo leer el Sheet: {e}")
        sys.exit(1)

    print(f"\nUsuarios a CREAR    ({len(nuevos)}):   {nuevos or '—ninguno—'}")
    print(f"Usuarios a ELIMINAR ({len(eliminar)}): {eliminar or '—ninguno—'}")

    if not nuevos and not eliminar:
        print("\nEl sheet está vacío. No hay nada que hacer.")
        return

    print("\n── Creando usuarios ──────────────────────")
    if nuevos:
        for u in nuevos:
            create_user_windows(u) if IS_WINDOWS else create_user_linux(u)
    else:
        print("  (ninguno)")

    print("\n── Eliminando usuarios ───────────────────")
    if eliminar:
        for u in eliminar:
            delete_user_windows(u) if IS_WINDOWS else delete_user_linux(u)
    else:
        print("  (ninguno)")

    # Vaciar el sheet una vez procesado todo
    print("\n── Vaciando el sheet ─────────────────────")
    try:
        clear_sheet(service)
    except Exception as e:
        print(f"  [ERROR] No se pudo vaciar el sheet: {e}")
        print("  Comprueba que la Service Account tiene rol de Editor en el sheet.")

    print("\n✔ Proceso completado.")


if __name__ == "__main__":
    main()
