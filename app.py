# import requests
# import pytz
# import json
# from datetime import datetime
# import tkinter as tk
# from tkinter import scrolledtext

# # URL y headers
# URL = "https://webapimarcacion.continental.edu.pe/api/marcacion/registrar"
# HEADERS = {
#     "apikey": "6bd4da79-7408-44e5-93fd-5da461a97873",
#     "Content-Type": "application/json"
# }

# # Horarios y tipos de marcación
# HORARIOS = {
#     "08:00:00": "ME",  # Mañana entrada
#     "13:00:00": "IR",  # Inicio refrigerio
#     "14:00:00": "FR",  # Fin refrigerio
#     "17:00:00": "MS"   # Mañana salida
# }

# # Zona horaria Lima
# zona_peru = pytz.timezone("America/Lima")

# # Lista para almacenar logs
# logs = []
# enviados_hoy = set()

# # Función para enviar marcación
# def enviar_marcacion(tipo):
#     fecha_hora = datetime.now(zona_peru).strftime("%Y-%m-%d %H:%M:%S")
#     payload = {
#         "compania": "02",
#         "correo": "rsinche@continental.edu.pe",
#         "fecha_hora": fecha_hora,
#         "tipo_marcacion": tipo
#     }

#     try:
#         resp = requests.post(URL, headers=HEADERS, json=payload)
#         log_msg = {
#             "fecha_envio": fecha_hora,
#             "data_enviada": payload,
#             "respuesta_status": resp.status_code,
#             "respuesta_texto": resp.text
#         }
#     except Exception as e:
#         log_msg = {
#             "fecha_envio": fecha_hora,
#             "data_enviada": payload,
#             "error": str(e)
#         }

#     logs.append(log_msg)
#     if len(logs) > 20:
#         logs.pop(0)
#     actualizar_logs()

# # Actualizar área de logs en formato JSON
# def actualizar_logs():
#     log_area.delete(1.0, tk.END)
#     for log in logs:
#         log_area.insert(tk.END, json.dumps(log, indent=4, ensure_ascii=False) + "\n\n")

# # Actualizar reloj cada segundo
# def actualizar_reloj():
#     ahora = datetime.now(zona_peru)
#     hora_actual = ahora.strftime("%H:%M:%S")
#     fecha_actual = ahora.strftime("%Y-%m-%d")

#     reloj_label.config(text=hora_actual)

#     # Verificar si es hora de marcar
#     if hora_actual in HORARIOS:
#         clave_envio = f"{fecha_actual}-{hora_actual}"
#         if clave_envio not in enviados_hoy:
#             tipo = HORARIOS[hora_actual]
#             enviar_marcacion(tipo)
#             enviados_hoy.add(clave_envio)

#     root.after(1000, actualizar_reloj)

# # --- Interfaz ---
# root = tk.Tk()
# root.title("Reloj de Marcación Automática - Lima, Perú")
# root.geometry("700x500")

# # Estilo reloj
# reloj_label = tk.Label(root, text="", font=("Arial", 40), fg="blue")
# reloj_label.pack(pady=20)

# # Área de logs
# log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, font=("Consolas", 10))
# log_area.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

# # Iniciar reloj
# actualizar_reloj()

# # Ejecutar app
# root.mainloop()


import customtkinter as ctk
import requests
import pytz
from datetime import datetime
import json
import math

# ====== CONFIG ======
API_URL = "https://webapimarcacion.continental.edu.pe/api/marcacion/registrar"
API_KEY = "6bd4da79-7408-44e5-93fd-5da461a97873"
CORREO = "rsinche@continental.edu.pe"
COMPANIA = "02"
TIMEZONE = pytz.timezone("America/Lima")

# Horarios y tipos
HORARIOS = {
    "08:00": "ME",
    "13:00": "IR",
    "14:00": "FR",
    "19:00": "MS"
}

# ====== APP ======
class RelojApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Reloj Marcador")
        self.geometry("400x500")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Estado
        self.logs_visible = True
        self.last_sent = None

        # Canvas para anillo
        self.canvas = ctk.CTkCanvas(self, width=300, height=300, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Botón toggle logs
        self.toggle_btn = ctk.CTkButton(self, text="Ocultar Logs", command=self.toggle_logs)
        self.toggle_btn.pack(pady=5)

        # Área de logs
        self.logs_text = ctk.CTkTextbox(self, width=360, height=150)
        self.logs_text.pack(pady=5)
        self.logs_text.insert("end", "=== LOGS DEL SISTEMA ===\n")

        # Inicia el loop
        self.actualizar_reloj()

    def toggle_logs(self):
        if self.logs_visible:
            self.logs_text.pack_forget()
            self.toggle_btn.configure(text="Mostrar Logs")
        else:
            self.logs_text.pack(pady=5)
            self.toggle_btn.configure(text="Ocultar Logs")
        self.logs_visible = not self.logs_visible

    def actualizar_reloj(self):
        # Hora actual Lima
        ahora = datetime.now(TIMEZONE)
        hora_str = ahora.strftime("%H:%M:%S")

        # Borrar y dibujar anillo
        self.canvas.delete("all")
        self.dibujar_anillo(ahora)

        # Dibujar hora en el centro
        self.canvas.create_text(150, 150, text=hora_str, fill="white", font=("Arial", 28, "bold"))

        # Comprobar si hay que enviar POST
        hora_minuto = ahora.strftime("%H:%M")
        if hora_minuto in HORARIOS:
            if self.last_sent != hora_minuto:
                self.enviar_post(HORARIOS[hora_minuto])
                self.last_sent = hora_minuto

        # Repetir cada 50ms para animación fluida
        self.after(50, self.actualizar_reloj)

    def dibujar_anillo(self, ahora):
        segundos_totales = ahora.minute * 60 + ahora.second + ahora.microsecond / 1_000_000
        angulo = (segundos_totales / 3600) * 360

        # Fondo del círculo
        self.canvas.create_oval(20, 20, 280, 280, outline="#444", width=10)

        # Arco de progreso
        self.canvas.create_arc(20, 20, 280, 280, start=90, extent=-angulo,
                               style="arc", outline="#ff7f50", width=10)

    def enviar_post(self, tipo):
        fecha_hora = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        payload = {
            "compania": COMPANIA,
            "correo": CORREO,
            "fecha_hora": fecha_hora,
            "tipo_marcacion": tipo
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": API_KEY
        }

        try:
            resp = requests.post(API_URL, headers=headers, json=payload)
            log_entry = {
                "fecha_envio": fecha_hora,
                "json_enviado": payload,
                "respuesta": resp.text
            }
            self.logs_text.insert("end", json.dumps(log_entry, indent=2, ensure_ascii=False) + "\n\n")
            self.logs_text.see("end")
        except Exception as e:
            self.logs_text.insert("end", f"[ERROR] {str(e)}\n")
            self.logs_text.see("end")

# Ejecutar app
if __name__ == "__main__":
    app = RelojApp()
    app.mainloop()
