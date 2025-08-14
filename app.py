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
            self.logs_text.pack(pady=10)
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
        # fecha_hora = "2025-08-13 08:00:00"

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
            }
            response_api = {
                "respuesta": resp.text,
                "codigo_estado": resp.status_code
            }
            
            self.logs_text.insert("end", json.dumps(log_entry, indent=2, ensure_ascii=False) + "\n\n")
            self.logs_text.insert("end", json.dumps(response_api, indent=2, ensure_ascii=False) + "\n\n")
            self.logs_text.see("end")
        except Exception as e:
            self.logs_text.insert("end", f"[ERROR] {str(e)}\n")
            self.logs_text.see("end")

# Ejecutar app
if __name__ == "__main__":
    app = RelojApp()
    app.mainloop()
