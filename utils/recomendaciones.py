def recomendar_progresion(series_df, ejercicio):
    if series_df.empty:
        return "Sin registros previos. Usa un peso moderado y deja 2 repeticiones en reserva."

    ult = series_df[series_df["ejercicio"] == ejercicio].copy()
    if ult.empty:
        return "Sin registros para este ejercicio. Empieza conservador y registra tus series."

    ult_fecha = sorted(ult["fecha"].unique())[-1]
    data = ult[ult["fecha"] == ult_fecha]

    try:
        rpe_prom = float(data["rpe"].mean())
        dolor_max = float(data["dolor_hombro"].max())
        reps_total = int(data["reps"].sum())
    except Exception:
        return "Hay registros, pero faltan datos para recomendar progresión."

    if dolor_max >= 6:
        return "Dolor alto registrado. No subas peso. Cambia a una variante segura o suspende ese ejercicio."
    if dolor_max >= 4:
        return "Dolor moderado registrado. Mantén o baja peso y revisa técnica/rango."
    if rpe_prom <= 8:
        return "Buen control. Si completaste tus reps objetivo, puedes subir ligeramente el peso la próxima vez."
    return "Mantén el peso actual hasta completar las reps con mejor control."
