const cron = require("node-cron");
const axios = require("axios");
const fs = require("fs");

// Zona horaria para Lima
const timeZone = "America/Lima";

// Función para enviar marcación
async function enviarMarcacion(tipo) {
  const fecha = new Date().toLocaleString("sv-SE", { timeZone });

  const payload = {
    compania: "02",
    correo: "rsinche@continental.edu.pe",
    fecha_hora: fecha,
    tipo_marcacion: tipo
  };

  try {
    const res = await axios.post(
      "https://webapimarcacion.continental.edu.pe/api/marcacion/registrar",
      payload,
      {
        headers: {
          "Content-Type": "application/json",
          "apikey": "6bd4da79-7408-44e5-93fd-5da461a97873"
        }
      }
    );

    const log = `[${fecha}] Tipo: ${tipo} - Respuesta: ${JSON.stringify(res.data)}\n`;
    fs.appendFileSync("logs.txt", log);
    console.log("Marcación enviada:", log);
  } catch (err) {
    const log = `[${fecha}] ERROR: ${err.message}\n`;
    fs.appendFileSync("logs.txt", log);
    console.error("Error al enviar marcación:", err.message);
  }
}

// Programar tareas en hora exacta Lima
cron.schedule("0 8 * * 1-5", () => enviarMarcacion("ME"), { timezone: timeZone }); // 8:00
cron.schedule("0 13 * * 1-5", () => enviarMarcacion("IR"), { timezone: timeZone }); // 13:00
cron.schedule("0 14 * * 1-5", () => enviarMarcacion("FR"), { timezone: timeZone }); // 14:00
cron.schedule("0 19 * * 1-5", () => enviarMarcacion("MS"), { timezone: timeZone }); // 19:00

console.log("Marcador automático activo. Esperando horarios...");