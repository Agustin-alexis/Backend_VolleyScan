"""Prueba rápida del panel: inicia sesión, muestra el dashboard, crea un equipo
de prueba (si no existe) y lista los equipos.

Uso (con el servidor encendido en otra terminal):
    python probar_panel.py

No guarda ni imprime tu contraseña ni el token.
"""
import getpass
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("PANEL_API", "http://127.0.0.1:8000/api")
NOMBRE_EQUIPO = "Equipo Prueba"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass


def llamar(metodo, ruta, datos=None, token=None):
    cuerpo = json.dumps(datos).encode("utf-8") if datos is not None else None
    peticion = urllib.request.Request(BASE + ruta, data=cuerpo, method=metodo)
    peticion.add_header("Content-Type", "application/json")
    if token:
        peticion.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(peticion, timeout=15) as respuesta:
            texto = respuesta.read().decode("utf-8")
            return respuesta.status, (json.loads(texto) if texto else None)
    except urllib.error.HTTPError as error:
        texto = error.read().decode("utf-8", "replace")
        try:
            return error.code, json.loads(texto)
        except ValueError:
            return error.code, texto[:300]
    except urllib.error.URLError as error:
        sys.exit(
            f"\nNo se pudo conectar ({error.reason}).\n"
            "¿Está encendido el servidor? En la otra terminal ejecuta: python manage.py runserver"
        )


def paso(titulo, estado, esperado):
    marca = "OK   " if estado == esperado else "FALLO"
    print(f"[{marca}] {titulo} (código {estado})")
    return estado == esperado


def main():
    email = input("Correo [entrenador@prueba.com]: ").strip() or "entrenador@prueba.com"
    clave = getpass.getpass("Contraseña (no se muestra al escribir): ")

    estado, datos = llamar("POST", "/auth/login", {"email": email, "password": clave})
    if not paso("Iniciar sesión", estado, 200):
        sys.exit(f"  Respuesta: {datos}")
    token = datos["access"]
    usuario = datos["usuario"]
    print(f"  Hola, {usuario['nombre']} {usuario['apellido']} (rol: {usuario['rol']})")

    estado, datos = llamar("GET", "/panel/dashboard", token=token)
    if paso("Dashboard", estado, 200):
        print(f"  Equipos activos: {datos['equipos_activos']} | "
              f"Deportistas: {datos['deportistas_activos']} | "
              f"Análisis pendientes: {datos['analisis_pendientes']}")
    else:
        print(f"  Respuesta: {datos}")

    estado, datos = llamar("GET", "/panel/equipos", token=token)
    if not paso("Listar equipos", estado, 200):
        sys.exit(f"  Respuesta: {datos}")

    if not any(e["nombre"] == NOMBRE_EQUIPO for e in datos["results"]):
        estado, creado = llamar(
            "POST", "/panel/equipos",
            {"nombre": NOMBRE_EQUIPO, "categoria": "Juvenil", "temporada": "2026"},
            token=token,
        )
        if not paso("Crear equipo de prueba", estado, 201):
            sys.exit(f"  Respuesta: {creado}")
        estado, datos = llamar("GET", "/panel/equipos", token=token)
        paso("Listar equipos otra vez", estado, 200)

    print(f"  Total de equipos: {datos['count']}")
    for equipo in datos["results"]:
        print(f"   - #{equipo['id']} {equipo['nombre']} ({equipo.get('categoria')}, "
            f"deportistas: {equipo.get('total_deportistas')})")

    print("\nListo: el login y los CRUD de equipos funcionan.")


if __name__ == "__main__":
    main()