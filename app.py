
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, date
import plotly.express as px
from utils.recomendaciones import recomendar_progresion

st.set_page_config(page_title="RecompFit JC", page_icon="💪", layout="wide")

DATA = Path("data")

def load_csv(name):
    path = DATA / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)

def save_csv(df, name):
    df.to_csv(DATA / name, index=False, encoding="utf-8-sig")

def add_row(name, row):
    df = load_csv(name)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    save_csv(df, name)

rutinas = load_csv("rutina_base.csv")
ejercicios = load_csv("ejercicios.csv")
series_log = load_csv("series.csv")
cubitt = load_csv("mediciones_cubitt.csv")
entrenamientos = load_csv("entrenamientos.csv")

st.sidebar.title("💪 RecompFit JC")
page = st.sidebar.radio(
    "Menú",
    ["Dashboard", "Rutina de hoy", "Registrar series", "Temporizador", "Biblioteca ejercicios", "Mediciones Cubitt", "Progreso", "Calendario / plan"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Objetivo: recomposición corporal, bajar grasa y proteger hombro izquierdo.")

def latest_cubitt():
    if cubitt.empty:
        return None
    temp = cubitt.copy()
    temp["fecha"] = pd.to_datetime(temp["fecha"], errors="coerce")
    temp = temp.sort_values("fecha")
    return temp.iloc[-1]

if page == "Dashboard":
    st.title("📊 Dashboard de recomposición corporal")
    ult = latest_cubitt()
    if ult is not None:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Peso actual", f"{ult['peso_kg']} kg")
        c2.metric("Grasa corporal", f"{ult['grasa_pct']}%")
        c3.metric("Masa muscular", f"{ult['masa_muscular_kg']} kg")
        c4.metric("Grasa visceral", f"{ult['grasa_visceral']}")
        c5,c6,c7,c8 = st.columns(4)
        c5.metric("IMC", f"{ult['imc']}")
        c6.metric("TMB", f"{ult['tmb_kcal']} kcal")
        c7.metric("Edad metabólica", f"{ult['edad_metabolica']}")
        c8.metric("Salud", f"{ult['puntuacion_salud']}")
    else:
        st.info("Todavía no hay mediciones Cubitt.")

    st.subheader("Estado semanal")
    c1,c2,c3 = st.columns(3)
    c1.info("Rutina recomendada: 3 días por semana")
    c2.info("Cardio recomendado: 15-20 min por sesión")
    c3.info("Pasos meta inicial: 5.000 diarios")

    st.subheader("Lectura de recomposición")
    st.write("""
    La recomposición corporal busca bajar grasa mientras mantienes o aumentas masa muscular.
    En tu caso, el foco es reducir grasa corporal y visceral, mejorar fuerza, cuidar el hombro izquierdo
    y sostener la progresión semanal.
    """)

elif page == "Rutina de hoy":
    st.title("🏋️ Rutina de hoy")
    dia = st.selectbox("Selecciona el día de rutina", ["Día A", "Día B", "Día C"])
    rutina_dia = rutinas[rutinas["dia"] == dia].sort_values("orden")
    nombre = rutina_dia["nombre_rutina"].iloc[0] if not rutina_dia.empty else ""
    st.subheader(f"{dia} — {nombre}")
    st.info("Calentamiento: 10 minutos de caminadora, bici o elíptica + movilidad suave de hombro.")

    for _, row in rutina_dia.iterrows():
        with st.expander(f"{int(row['orden'])}. {row['ejercicio']} — {row['series']} x {row['reps_objetivo']}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"**Descanso:** {row['descanso_seg']} segundos")
                st.write(f"**Observación:** {row['observacion']}")
                info = ejercicios[ejercicios["ejercicio"] == row["ejercicio"]]
                if not info.empty:
                    info = info.iloc[0]
                    st.write(f"**Grupo:** {info['grupo']}")
                    st.write(f"**Músculo principal:** {info['musculo_principal']}")
                    st.write(f"**Riesgo hombro:** {info['riesgo_hombro']}")
                    st.write(f"**Instrucciones:** {info['instrucciones']}")
                    st.write(f"**Evitar:** {info['errores_comunes']}")
                    st.write(f"**Sustitución:** {info['sustitucion']}")
            with col2:
                st.warning(recomendar_progresion(series_log, row["ejercicio"]))
                st.caption("Espacio para imagen/GIF del ejercicio. Luego se agregan archivos en assets/ejercicios.")

    st.success("Cardio final sugerido: 15 a 20 minutos moderado.")

elif page == "Registrar series":
    st.title("📝 Registrar series")
    with st.form("registro_series"):
        fecha = st.date_input("Fecha", value=date.today())
        dia = st.selectbox("Día de rutina", ["Día A", "Día B", "Día C"])
        ejercicios_dia = rutinas[rutinas["dia"] == dia]["ejercicio"].tolist()
        ejercicio = st.selectbox("Ejercicio", ejercicios_dia)
        serie = st.number_input("Serie", min_value=1, max_value=10, value=1)
        peso = st.number_input("Peso usado", min_value=0.0, value=0.0, step=0.5)
        reps = st.number_input("Repeticiones logradas", min_value=0, value=10, step=1)
        rpe = st.slider("Esfuerzo RPE 1-10", 1, 10, 7)
        dolor = st.slider("Dolor hombro 0-10", 0, 10, 0)
        obs = st.text_input("Observación")
        submitted = st.form_submit_button("Guardar serie")
        if submitted:
            add_row("series.csv", {
                "fecha": str(fecha), "dia": dia, "ejercicio": ejercicio, "serie": serie,
                "peso": peso, "reps": reps, "rpe": rpe, "dolor_hombro": dolor, "observacion": obs
            })
            st.success("Serie guardada. Recarga la página para ver el registro actualizado.")

    st.subheader("Últimos registros")
    series_log = load_csv("series.csv")
    if not series_log.empty:
        st.dataframe(series_log.tail(20), use_container_width=True)
    else:
        st.info("Sin registros todavía.")

elif page == "Temporizador":
    st.title("⏱️ Temporizador de descanso")
    st.write("Selecciona el descanso y presiona iniciar. En Streamlit el contador es visual; en una PWA/app móvil se puede mejorar con vibración o push.")
    seconds = st.selectbox("Descanso", [45,60,75,90,120], index=3)
    st.components.v1.html(f"""
    <div style="font-family: Arial; text-align:center;">
        <h2>Descanso: <span id="time">{seconds}</span> segundos</h2>
        <button onclick="startTimer()" style="font-size:18px;padding:10px 20px;">Iniciar</button>
        <button onclick="resetTimer()" style="font-size:18px;padding:10px 20px;">Reiniciar</button>
    </div>
    <script>
    let start = {seconds};
    let remaining = start;
    let interval = null;
    function render() {{
        document.getElementById("time").innerText = remaining;
    }}
    function startTimer() {{
        if (interval) clearInterval(interval);
        interval = setInterval(function() {{
            remaining -= 1;
            render();
            if (remaining <= 0) {{
                clearInterval(interval);
                alert("Descanso terminado");
                remaining = start;
                render();
            }}
        }}, 1000);
    }}
    function resetTimer() {{
        if (interval) clearInterval(interval);
        remaining = start;
        render();
    }}
    </script>
    """, height=220)

elif page == "Biblioteca ejercicios":
    st.title("📚 Biblioteca de ejercicios")
    grupo = st.selectbox("Filtrar por grupo", ["Todos"] + sorted(ejercicios["grupo"].dropna().unique().tolist()))
    data = ejercicios if grupo == "Todos" else ejercicios[ejercicios["grupo"] == grupo]
    for _, e in data.iterrows():
        with st.expander(f"{e['ejercicio']} — Riesgo hombro: {e['riesgo_hombro']}"):
            st.write(f"**Equipo:** {e['equipo']}")
            st.write(f"**Músculo principal:** {e['musculo_principal']}")
            st.write(f"**Cómo hacerlo:** {e['instrucciones']}")
            st.write(f"**Errores comunes:** {e['errores_comunes']}")
            st.write(f"**Sustitución:** {e['sustitucion']}")
            st.caption("Aquí se puede insertar una imagen o GIF del ejercicio.")

elif page == "Mediciones Cubitt":
    st.title("⚖️ Mediciones Cubitt")
    with st.form("cubitt_form"):
        fecha = st.date_input("Fecha", value=date.today())
        c1,c2,c3 = st.columns(3)
        peso_kg = c1.number_input("Peso kg", value=94.6, step=0.1)
        grasa_pct = c2.number_input("Grasa %", value=29.0, step=0.1)
        masa_muscular_kg = c3.number_input("Masa muscular kg", value=63.8, step=0.1)
        c4,c5,c6 = st.columns(3)
        grasa_visceral = c4.number_input("Grasa visceral", value=13.0, step=0.1)
        imc = c5.number_input("IMC", value=31.2, step=0.1)
        tmb_kcal = c6.number_input("TMB kcal", value=1820, step=10)
        c7,c8,c9 = st.columns(3)
        agua_pct = c7.number_input("Agua %", value=51.3, step=0.1)
        edad_metabolica = c8.number_input("Edad metabólica", value=49, step=1)
        cintura_cm = c9.text_input("Cintura cm opcional")
        submitted = st.form_submit_button("Guardar medición")
        if submitted:
            add_row("mediciones_cubitt.csv", {
                "fecha": str(fecha), "peso_kg": peso_kg, "grasa_pct": grasa_pct,
                "masa_grasa_kg": "", "imc": imc, "musculo_esqueletico_pct": "",
                "masa_muscular_kg": masa_muscular_kg, "proteina_pct": "",
                "tmb_kcal": tmb_kcal, "peso_sin_grasa_kg": "",
                "grasa_subcutanea_pct": "", "grasa_visceral": grasa_visceral,
                "agua_pct": agua_pct, "masa_agua_kg": "", "masa_osea_kg": "",
                "puntuacion_salud": "", "edad_metabolica": edad_metabolica,
                "cintura_cm": cintura_cm
            })
            st.success("Medición guardada. Recarga la página para actualizar gráficos.")

    cubitt = load_csv("mediciones_cubitt.csv")
    st.subheader("Histórico")
    st.dataframe(cubitt.tail(20), use_container_width=True)

elif page == "Progreso":
    st.title("📈 Progreso")
    tab1, tab2 = st.tabs(["Composición corporal", "Fuerza por ejercicio"])

    with tab1:
        cubitt = load_csv("mediciones_cubitt.csv")
        if not cubitt.empty:
            cubitt["fecha"] = pd.to_datetime(cubitt["fecha"], errors="coerce")
            metric = st.selectbox("Métrica", ["peso_kg","grasa_pct","masa_muscular_kg","grasa_visceral","imc","agua_pct","edad_metabolica"])
            fig = px.line(cubitt.sort_values("fecha"), x="fecha", y=metric, markers=True, title=f"Evolución: {metric}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin mediciones.")

    with tab2:
        series_log = load_csv("series.csv")
        if not series_log.empty:
            series_log["fecha"] = pd.to_datetime(series_log["fecha"], errors="coerce")
            ejercicio = st.selectbox("Ejercicio", sorted(series_log["ejercicio"].dropna().unique().tolist()))
            data = series_log[series_log["ejercicio"] == ejercicio].copy()
            data["volumen"] = data["peso"] * data["reps"]
            resumen = data.groupby("fecha", as_index=False).agg(peso_max=("peso","max"), reps_total=("reps","sum"), volumen_total=("volumen","sum"))
            fig = px.line(resumen, x="fecha", y="peso_max", markers=True, title=f"Peso máximo registrado: {ejercicio}")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(resumen, use_container_width=True)
        else:
            st.info("Registra series para ver progreso de fuerza.")

elif page == "Calendario / plan":
    st.title("🗓️ Calendario y plan")
    st.write("Plan recomendado inicial:")
    st.table(pd.DataFrame([
        ["Lunes o martes", "Día A", "60 min"],
        ["Miércoles o jueves", "Día B", "60 min"],
        ["Viernes o sábado", "Día C", "60 min"],
    ], columns=["Día sugerido", "Rutina", "Duración"]))
    st.subheader("Recordatorios sugeridos")
    st.write("""
    - Entrenar 3 días por semana.
    - Registrar Cubitt 1 vez por semana, idealmente mismo día y hora.
    - Caminar meta inicial: 5.000 pasos diarios.
    - Revisar progreso cada 4 semanas.
    """)
    st.info("Para notificaciones reales en celular, la siguiente fase sería convertir esta lógica a PWA/app móvil o integrarla con Google Calendar/Telegram.")
