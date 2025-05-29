
import streamlit as st
import pandas as pd
import numpy as np
import os
import zipfile
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, ttest_ind
from scipy.signal import find_peaks

st.set_page_config(layout="wide")
sns.set(style="whitegrid")

# Función para calcular eta squared
def calcular_eta_squared(df, columna, grupo):
    grand_mean = df[columna].mean()
    ss_total = ((df[columna] - grand_mean) ** 2).sum()
    ss_between = sum([
        len(g) * (g[columna].mean() - grand_mean) ** 2
        for _, g in df.groupby(grupo)
    ])
    return ss_between / ss_total if ss_total > 0 else 0

st.title("AVANCE3 · Análisis Unificado de Biosensores")

uploaded_files = st.file_uploader("Carga tus archivos CSV", accept_multiple_files=True, type="csv")

df_eye, df_fea, df_gsr = None, None, None

for file in uploaded_files:
    content = pd.read_csv(file)
    if "ET_TimeSignal" in content.columns:
        df_eye = content.copy()
    elif "Valence" in content.columns:
        df_fea = content.copy()
    elif "GSR Conductance CAL" in content.columns:
        df_gsr = content.copy()

# EYETRACKING
if df_eye is not None:
    st.header("🔵 Eyetracking")

    df_eye_fix = df_eye[df_eye["EventSource_1"] == 1].copy()
    df_eye_fix["ET_TimeSignal"] = pd.to_numeric(df_eye_fix["ET_TimeSignal"], errors="coerce")
    df_eye_fix = df_eye_fix.dropna(subset=["ET_TimeSignal"])

    resumen_eyetrack = []
    for (stim, participant), grupo in df_eye_fix.groupby(["SourceStimuliName", "Participant"]):
        tiempos = grupo["ET_TimeSignal"].sort_values()
        dwell = tiempos.max() - tiempos.min()
        ttff = tiempos.min()
        n_fix = len(tiempos)
        resumen_eyetrack.append({
            "Estímulo": stim,
            "Participante": participant,
            "Tiempo_Permanencia": dwell,
            "TTFF": ttff,
            "N_Fijaciones": n_fix
        })

    tabla_eyetrack = pd.DataFrame(resumen_eyetrack)
    st.subheader("Tabla de métricas por estímulo")
    st.dataframe(tabla_eyetrack)

    tabla_resumen_estad = tabla_eyetrack.groupby("Estímulo").agg({
        "Tiempo_Permanencia": ["mean", "std"],
        "TTFF": ["mean", "std"],
        "N_Fijaciones": ["mean", "std"]
    }).reset_index()
    tabla_resumen_estad.columns = ["Estímulo", "Dwell_Media", "Dwell_SD", "TTFF_Media", "TTFF_SD", "Fijaciones_Media", "Fijaciones_SD"]

    st.subheader("Resumen estadístico")
    st.dataframe(tabla_resumen_estad)

    anova_dwell = f_oneway(*[g["Tiempo_Permanencia"].values for _, g in tabla_eyetrack.groupby("Estímulo")])
    eta_dwell = calcular_eta_squared(tabla_eyetrack, "Tiempo_Permanencia", "Estímulo")
    st.markdown(f"**ANOVA Dwell:** F = {anova_dwell.statistic:.4f}, p = {anova_dwell.pvalue:.4f}, η² = {eta_dwell:.4f}")

# GSR
if df_gsr is not None:
    st.header("🟢 GSR")
    resumen_gsr = []
    for stim, grupo in df_gsr.groupby("SourceStimuliName"):
        signal = grupo["GSR Conductance CAL"].dropna().values
        peaks, props = find_peaks(signal, height=0.02)
        amplitudes = props["peak_heights"]
        resumen_gsr.append({
            "Estímulo": stim,
            "Núm_Picos": len(peaks),
            "Amp_Media": np.mean(amplitudes) if len(amplitudes) > 0 else 0,
            "Amp_SD": np.std(amplitudes) if len(amplitudes) > 0 else 0
        })
    tabla_gsr = pd.DataFrame(resumen_gsr)
    st.subheader("Tabla GSR")
    st.dataframe(tabla_gsr)

# FEA
if df_fea is not None:
    st.header("🔴 FEA")
    emociones = ['Anger', 'Contempt', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise']
    df_fea['Engagement_Promedio'] = df_fea[emociones].mean(axis=1)
    df_fea['Valence_Class'] = df_fea['Valence'].apply(lambda x: 'Positiva' if x > 0 else ('Negativa' if x < 0 else 'Neutra'))

    tabla_resumen = df_fea.groupby('SourceStimuliName').agg({
        'Valence': ['mean', 'std'],
        'Engagement_Promedio': ['mean', 'std']
    }).reset_index()
    tabla_resumen.columns = ['Estímulo', 'Valencia_Media', 'Valencia_SD', 'Engagement_Media', 'Engagement_SD']

    st.subheader("Resumen FEA")
    st.dataframe(tabla_resumen)

    groups_val = [g["Valence"].dropna() for _, g in df_fea.groupby("SourceStimuliName") if len(g["Valence"].dropna()) > 1]
    if len(groups_val) > 1:
        anova_valencia = f_oneway(*groups_val)
        f2_val = anova_valencia.statistic / (anova_valencia.statistic + df_fea.shape[0] - 1)
        st.markdown(f"**ANOVA Valencia:** F = {anova_valencia.statistic:.4f}, p = {anova_valencia.pvalue:.4f}, F² = {f2_val:.4f}")
