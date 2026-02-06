from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Footer, Input, Button, Static, Select
from textual.reactive import reactive
import random
from supabase import create_client
from dotenv import load_dotenv
import os
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("❌ Faltan variables SUPABASE_URL o SUPABASE_KEY en el archivo .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class MonitorApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Sistema de Monitoreo Industrial"
    SUB_TITLE = "TUI Python + FastAPI + PostgreSQL"

    status = reactive("IDLE")

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="main"):
            yield Static("📡 Sistema de Monitoreo CNC", id="title")

            with Horizontal():
                yield Input(placeholder="Machine ID", id="machine", value="ST10")
                yield Select(
                    [("RUN", "RUN"), ("IDLE", "IDLE"), ("FAULT", "FAULT")],
                    value="IDLE",
                    id="status"
                )

            with Horizontal():
                yield Input(placeholder="Temperatura (°C)", id="temp")
                yield Input(placeholder="Humedad (%)", id="hum")

            with Horizontal():
                yield Input(placeholder="Vibración (g)", id="vib")
                yield Input(placeholder="RPM", id="rpm")

            with Horizontal():
                yield Input(placeholder="Corriente (A)", id="current")

            with Horizontal(id="buttons"):
                yield Button("📤 Enviar", id="send", variant="success")
                yield Button("🎲 Simular", id="simulate", variant="primary")
                yield Button("🧹 Limpiar", id="clear", variant="warning")

            yield Static("", id="log")

        yield Footer()

    # ------------------ Eventos ------------------

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "simulate":
            self.simulate_data()

        elif event.button.id == "send":
            self.send_data()

        elif event.button.id == "clear":
            self.clear_inputs()

    # ------------------ Lógica ------------------

    def simulate_data(self):
        self.query_one("#temp").value = f"{random.uniform(22, 30):.2f}"
        self.query_one("#hum").value = f"{random.uniform(35, 55):.2f}"
        self.query_one("#vib").value = f"{random.uniform(0.1, 0.6):.3f}"
        self.query_one("#rpm").value = str(random.randint(1600, 2200))
        self.query_one("#current").value = f"{random.uniform(2.5, 5.5):.2f}"
        self.query_one("#status").value = random.choice(["RUN", "IDLE", "FAULT"])

        self.write_log("🎲 Datos simulados correctamente")

    def send_data(self):
        data = self.collect_data()

        if not data:
            return

        try:
            supabase.table("machine_readings").insert(data).execute()
            self.write_log("📡 Datos enviados correctamente a Supabase")
        except Exception as e:
            self.write_log(f"❌ Error al enviar a Supabase: {e}", error=True)

    def collect_data(self):
        try:
            return {
                "machine_id": self.query_one("#machine").value,
                "temperature": float(self.query_one("#temp").value),
                "humidity": float(self.query_one("#hum").value),
                "vibration": float(self.query_one("#vib").value),
                "rpm": int(self.query_one("#rpm").value),
                "current": float(self.query_one("#current").value),
                "status": self.query_one("#status").value
            }
        except ValueError:
            self.write_log("❌ Error: Valores inválidos", error=True)
            return None

    def clear_inputs(self):
        for field in ["#temp", "#hum", "#vib", "#rpm", "#current"]:
            self.query_one(field).value = ""

        self.write_log("🧹 Campos limpiados")

    def write_log(self, message, error=False):
        log = self.query_one("#log")
        prefix = "🚨" if error else "✅"
        log.update(f"{prefix} {message}")


if __name__ == "__main__":
    MonitorApp().run()