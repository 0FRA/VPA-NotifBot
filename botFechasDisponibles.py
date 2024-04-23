import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
from sendMail import enviarAviso

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Constantes
FECHA_LIMITE = "26/04/2024"  # Fecha límite para buscar turnos disponibles
PLANTA = "110"  # ID de la planta de verificación vehicular de la ciudad de La Plata


def obtener_fechas_disponibles():
    URL = "https://pagoverificacion.sivef.com.ar/turnero-turnos.php"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "es-US,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "dnt": "1",
        "origin": "https://pagoverificacion.sivef.com.ar",
        "referer": "https://pagoverificacion.sivef.com.ar/turnero-modifica.php?tag=PROVINCIA",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    data = {
        "data": '[{"name":"action","value":"SELECCIONA-PLANTA"},{"name":"planta","value":"%s"}]'
        % PLANTA
    }

    response = requests.post(URL, headers=headers, data=data)
    response_data = json.loads(response.text)
    return response_data["data"]["fechas"]


def encontrar_fecha_con_saldo(fechas):
    DATE_FORMAT = "%d/%m/%Y"
    comparison_date = datetime.strptime(FECHA_LIMITE, DATE_FORMAT)
    for fecha_info in fechas:
        fecha = fecha_info["fecha"]
        saldo_fecha = int(fecha_info["saldo_fecha"])

        fecha_parts = fecha.split("/")
        fecha_dd_mm_yyyy = (
            f"{fecha_parts[0].zfill(2)}/{fecha_parts[1].zfill(2)}/{fecha_parts[2]}"
        )
        fecha_datetime = datetime.strptime(fecha_dd_mm_yyyy, DATE_FORMAT)

        if fecha_datetime < comparison_date and saldo_fecha > 0:
            return fecha_dd_mm_yyyy, saldo_fecha

    return None, None


def obtener_horarios_disponibles(fecha):
    url = "https://pagoverificacion.sivef.com.ar/turnero-turnos.php"
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "es-US,es;q=0.9,en-US;q=0.8,en;q=0.7,es-419;q=0.6",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "dnt": "1",
        "origin": "https://pagoverificacion.sivef.com.ar",
        "referer": "https://pagoverificacion.sivef.com.ar/turnero-modifica.php?tag=PROVINCIA",
        "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    data = {
        "data": '[{"name":"action","value":"SELECCIONA-FECHA"},{"name":"planta","value":"%s"},{"name":"fecha","value":"%s"}]'
        % (PLANTA, fecha)
    }

    response = requests.post(url, headers=headers, data=data)
    response_data = response.json()  # Aquí se accede al contenido JSON de la respuesta

    return response_data["data"]["horas"]


def encontrar_horario_disponible(horarios):
    # Verificar si hay horarios disponibles entre 8:00 y 9:00 con saldo > 0
    horarios_8_a_9 = any(
        hora["hora"] >= "08:00:00"
        and hora["hora"] <= "09:00:00"
        and int(hora["saldo"]) > 0
        for hora in horarios
    )

    # Verificar si hay horarios disponibles después de las 15:00 horas con saldo > 0
    horarios_despues_15 = any(
        hora["hora"] >= "15:00:00" and int(hora["saldo"]) > 0 for hora in horarios
    )

    # Devolver los resultados
    return horarios_8_a_9, horarios_despues_15


def main():
    fechas = obtener_fechas_disponibles()
    fecha_con_saldo, saldo_disponible = encontrar_fecha_con_saldo(fechas)

    if fecha_con_saldo:
        print(
            f"Hay saldo_fecha disponible para la fecha {fecha_con_saldo} con una cantidad de {saldo_disponible}."
        )
        message = f"\n\nSe encontró {saldo_disponible} turno disponible para la fecha {fecha_con_saldo}."

        enviarAviso(os.getenv("EMAIL_RECEIVER"), message, "[VPA] ¡Hay turnos libres!")
        enviarAviso(os.getenv("EMAIL_RECEIVER_2"), message, "[VPA] ¡Hay turnos libres!")

        horarios = obtener_horarios_disponibles(fecha_con_saldo)
        horarios_8_a_9, horarios_despues_15 = encontrar_horario_disponible(horarios)
        if horarios_8_a_9:
            print(
                f"Hay horarios disponibles entre las 8:00 y 9:00 para la fecha {fecha_con_saldo}."
            )
            horarios_disponibles = [
                hora["rango_horario"]
                for hora in horarios
                if hora["hora"] >= "08:00:00"
                and hora["hora"] < "09:00:00"
                and int(hora["saldo"]) > 0
            ]
            message = f"\n\nSe encontró {saldo_disponible} turno disponible para la fecha {fecha_con_saldo}.\n\nHorarios disponibles entre las 8:00 y 9:00:\n{', '.join(horarios_disponibles)}"
            enviarAviso(
                os.getenv("EMAIL_RECEIVER"), message, "[VPA] ¡Hay turnos libres!"
            )
            enviarAviso(
                os.getenv("EMAIL_RECEIVER_2"), message, "[VPA] ¡Hay turnos libres!"
            )
        if horarios_despues_15:
            print(
                f"Hay horarios disponibles después de las 15:00 para la fecha {fecha_con_saldo}."
            )
            horarios_disponibles = [
                hora["rango_horario"]
                for hora in horarios
                if hora["hora"] >= "15:00:00" and int(hora["saldo"]) > 0
            ]
            message = f"\n\nSe encontró {saldo_disponible} turno disponible para la fecha {fecha_con_saldo}.\n\nHorarios disponibles después de las 15:00:\n{', '.join(horarios_disponibles)}"
            enviarAviso(
                os.getenv("EMAIL_RECEIVER"), message, "[VPA] ¡Hay turnos libres!"
            )
            enviarAviso(
                os.getenv("EMAIL_RECEIVER_2"), message, "[VPA] ¡Hay turnos libres!"
            )
    else:
        print(f"No hay saldo_fecha disponible antes del {FECHA_LIMITE}.")


if __name__ == "__main__":
    main()
