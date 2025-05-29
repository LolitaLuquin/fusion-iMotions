
# AVANCE3 - Análisis de Biosensores (Eyetracking, GSR, FEA)

Esta aplicación permite cargar, analizar y visualizar datos de biosensores (Eyetracking, GSR y FEA) de iMotions en una interfaz unificada y dinámica.

## 📦 Requisitos

Instala las dependencias necesarias usando:

```bash
pip install -r requirementsAVANCE3.txt
```

## 🚀 Ejecución

Corre la aplicación con Streamlit:

```bash
streamlit run appAVANCE3.py
```

## 📂 Estructura esperada

Se espera que cargues archivos `.csv` exportados desde iMotions con los encabezados correctos a partir de las filas correspondientes:
- **Eyetracking y FEA:** encabezado en la fila 26 (índice 25)
- **GSR:** encabezado en la fila 28 (índice 27)

## 📈 Funcionalidades

1. Carga de múltiples archivos por tipo (Eyetracking, FEA, GSR).
2. Visualización de tablas estadísticas con:
   - ANOVA
   - p-value
   - F-squared
   - Desviación estándar
3. Gráficas dinámicas y comparativas:
   - Boxplots
   - Violin plots
   - Histograma con KDE
   - Heatmaps (para GSR)
4. Descarga de:
   - Archivos `.csv` de tablas
   - Archivos `.txt` con estadísticas
   - Archivos `.zip` con gráficas

## ✍️ Autoría

Desarrollado por Lolita Luquín y ChatGPT (OpenAI) como parte del Proyecto Terminal ECID.

