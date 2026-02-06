import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dashboard Industrial", layout="wide")

st.title("📊 Dashboard de Monitoreo Industrial")

# Obtener datos
response = supabase.table("machine_readings") \
    .select("*") \
    .order("created_at", desc=True) \
    .limit(100) \
    .execute()

df = pd.DataFrame(response.data)

if df.empty:
    st.warning("No hay datos aún")
    st.stop()

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

last = df.iloc[0]

col1.metric("🌡 Temperatura", f"{last['temperature']} °C")
col2.metric("💧 Humedad", f"{last['humidity']} %")
col3.metric("⚙ RPM", f"{last['rpm']}")
col4.metric("🔌 Corriente", f"{last['current']} A")
col5.metric("📡 Estado", last["status"])

# Gráficas
st.subheader("📈 Tendencias")

c1, c2 = st.columns(2)

with c1:
    st.line_chart(df.sort_values("created_at")["temperature"])

with c2:
    st.line_chart(df.sort_values("created_at")["vibration"])

# Tabla
st.subheader("📋 Historial")

st.dataframe(df.sort_values("created_at", ascending=False))