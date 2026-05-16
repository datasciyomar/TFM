# MVP Clínico — HCT Survival Predictor

**Prototipo interactivo** del TFM *"Predicción de Supervivencia Post-HCT y Equidad Racial"*  
Máster en Epidemiología y Salud Pública · VIU 2024-25

---

## Requisitos previos (macOS / MacBook Pro)

- macOS 12 Monterey o superior
- Python 3.10 (recomendado via `pyenv` o Homebrew)
- Visual Studio Code con extensión Python
- Los modelos entrenados (generados por NB04 y NB05)

---

## Instalación paso a paso

### 1. Clonar / copiar el proyecto

```bash
# Si usas GitHub:
git clone https://github.com/tu-usuario/tfm-hct-survival-equity.git
cd tfm-hct-survival-equity

# O simplemente navegar a la carpeta del proyecto en VS Code
```

### 2. Crear entorno virtual

```bash
# Desde el terminal de VS Code (Ctrl+`)
python3.10 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias del MVP

```bash
pip install --upgrade pip
pip install -r mvp_hct/requirements_app.txt
```

> **Nota para Apple Silicon (M1/M2/M3):** Si `scikit-survival` falla en la instalación,
> prueba primero con:
> ```bash
> pip install cmake
> pip install scikit-survival==0.23.0 --no-build-isolation
> ```

### 4. Estructura de archivos necesaria

Asegúrate de que los modelos y datos generados por los notebooks están en su lugar:

```
tfm-hct-survival-equity/
├── mvp_hct/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_Predictor.py
│   │   ├── 2_Equidad.py
│   │   └── 3_SHAP.py
│   ├── src/
│   │   ├── model_loader.py
│   │   └── preprocessing.py
│   ├── assets/              ← logo (opcional)
│   └── requirements_app.txt
├── models/                  ← generados por NB04
│   ├── xgb_aft_model.ubj
│   ├── rsf_model.pkl
│   ├── xgb_risk_val.npy
│   └── rsf_risk_val.npy
└── data/
    └── processed/           ← generados por NB02
        ├── X_val.parquet
        ├── race_val.parquet
        ├── y_time_val.npy
        ├── y_event_val.npy
        └── pipeline_objects.pkl
```

> **Sin modelos:** La app funciona en **modo demo** con predicciones simuladas.
> Útil para probar la interfaz antes de tener los modelos listos.

### 5. Ejecutar la aplicación

```bash
# Desde la raíz del proyecto, con el entorno activado:
cd mvp_hct
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501` en tu navegador.

---

## Uso en VS Code

1. Abre la carpeta del proyecto en VS Code
2. Selecciona el intérprete Python del entorno virtual (`.venv`)
3. Abre el terminal integrado (`Ctrl+\``)
4. Activa el entorno: `source .venv/bin/activate`
5. Navega a `mvp_hct/`: `cd mvp_hct`
6. Ejecuta: `streamlit run app.py`

Para **depuración** en VS Code, crea `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Streamlit: HCT MVP",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": ["run", "${workspaceFolder}/mvp_hct/app.py"],
      "justMyCode": true
    }
  ]
}
```

---

## Páginas de la aplicación

| Página | URL | Descripción |
|---|---|---|
| Inicio | `/` | Bienvenida, métricas globales, navegación |
| Predictor | `/Predictor` | Formulario clínico → predicción individual + SHAP waterfall |
| Equidad | `/Equidad` | C-index por raza, IC bootstrap, mecanismos estructurales |
| Interpretabilidad | `/SHAP` | Beeswarm global, heatmap por raza, dependence plots |

---

## Solución de problemas comunes

**`ModuleNotFoundError: No module named 'src'`**
→ Ejecutar siempre desde dentro de la carpeta `mvp_hct/`, no desde la raíz.

**`FileNotFoundError: xgb_aft_model.ubj`**
→ Los modelos no están generados. Ejecuta el NB04 primero, o usa el modo demo.

**Puerto 8501 ocupado**
→ `streamlit run app.py --server.port 8502`

**Lentitud en el primer arranque**
→ Normal: los modelos se cargan en memoria la primera vez. Streamlit los mantiene en caché.

**Apple Silicon: error de compilación en scikit-survival**
→ Ver instrucciones de instalación alternativa más arriba.

---

## Aviso

Esta aplicación es un **prototipo académico** desarrollado exclusivamente para el TFM.
No ha sido validada clínicamente de forma prospectiva y no debe utilizarse para
tomar decisiones clínicas reales sin validación externa independiente.
