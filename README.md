# Fall Detection using ADXL345 and STM32F103

## 1. Introduction

The project aims to detect falls using the ADXL345 accelerometer and the
STM32F103 microcontroller.\
Sensor data is transmitted to a computer via USB, where it can be
analyzed and visualized.\
Two approaches were developed: 
1. **Manual algorithm** - based on thresholds and sensor sample analysis
2. **Machine learning model** - based on a classifier trained on datasets collected from the sensor

The most important manual changes in the source code are located in: 
- `main.c` - main program logic, fall detection, parameter configuration. 
- `adxl345.c` - communication handling with the ADXL345 sensor.

Other files were generated and automatically modified by STM32CubeIDE.

## 2. Development Environment

- **STM32CubeIDE** - the main development environment for STM32F103 configuration and coding.
- **Additional tools** - Python 3.11, libraries: `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `xgboost`, `joblib`, `csv`, `serial`, `pyqtgraph`, `PyQt5`

## 3. Project Setup Instructions

1.  In STM32CubeIDE, select the correct microcontroller (STM32F103).
2.  Configure inputs/outputs and communication interfaces:
    -   I2C for communication with ADXL345,
    -   USB (CDC) for data transfer to PC.
3.  Flash the program to the microcontroller.
4.  Run one of the Python programs:
    -   `rx_adxl.py` -- for console data readout,
    -   `rx_adxl_visualization.py` -- for real-time visualization,
    -   `rx_adxl_with_ml.py` -- for combining manual algorithm and ML
        model.
5.  Python programs are stopped with `Ctrl+C` (**KeyInterrupt**). Data is automatically saved into a `.csv` file.
6.  Data can then be analyzed in Jupyter Notebook.

## 4. Communication

Two communication buses are used in this project: 
- **I2C** - between ADXL345 accelerometer and STM32 microcontroller,
- **USB** (CDC) - between STM32 and PC. Measurement data is cyclically transmitted to the PC and can be processed in various ways.

## 5. Data Reception Programs

### 5.1. `rx_adxl.py`

Python script for reading and displaying data in the console.

``` text
X, Y, Z, FALL
7.27, -7.31, 0.99, 0
7.27, -7.31, 0.99, 0
7.27, -7.31, 0.99, 0
7.27, -7.31, 0.96, 0
```

### 5.2. `rx_adxl_visualization.py`

Program for real-time visualization of sensor data.
![Visualization](Plots/vis.png)
### 5.3. `rx_adxl_with_ml.py` 
Program combining manual algorithm with ML model prediction.

``` text
X=-3.86, Y=5.01, Z=-3.48, FALL_HW=0

--- WINDOW #34 ---
{'X_mean': 5.46, 'Y_mean': -1.98, 'Z_mean': 5.33, 'A_mean': 9.45, 'DX_mean': -0.09, 'DY_mean': 0.07, 'DZ_mean': -0.07, 'DA_mean': -0.04, 'FALL': 0}
ML Prediction: 0
---------------
```

## 6. Manual Algorithm

The manual implementation used simple conditions: 
- if acceleration dropped below `FREEFALL_LIMIT_MS2`, a counter `freeFallCount` was
incremented,
- the counter was reset if the signal returned to normal faster than `FREEFALL_MIN_SAMPLES`,
- an additional condition `IMPACT_DELTA_MIN` required a minimum difference between consecutive samples to avoid false triggers from hand waving,
- after a fall, a quick peak above `IMPACT_THRESHOLD` had to follow.

Detection parameters:
``` c
#define FREEFALL_LIMIT_MS2   6.0f
#define FREEFALL_MIN_SAMPLES 200
#define IMPACT_THRESHOLD     50.0f
#define IMPACT_DELTA_MIN     20.0f
#define DEBOUNCE_TIME_MS     1000
```

### Limitations of the manual algorithm

-   sensitivity to chosen threshold values,
-   difficulty in distinguishing unusual movements from real falls,
-   possible false positives from rapid hand movements.

## 7. Machine Learning

### 7.1. Time Windows

A single `X, Y, Z` sample is not enough. Instead, **time windows** (150-160 samples) were used. From each window, statistical features were calculated to capture **signal dynamics over time**, not just instantaneous values.

### 7.2. Extracted Features

For each axis **X, Y, Z** and derived signals: 
- **A** - total acceleration $\sqrt{X^2 + Y^2 + Z^2}$,
- **DX, DY, DZ, DA** - differences between consecutive samples,

``` python
df = pd.read_csv('data/new_data.csv')
df["A"] = np.sqrt(df["X"]**2 + df["Y"]**2 + df["Z"]**2)
df["DX"] = df["X"].diff().fillna(0)
df["DY"] = df["Y"].diff().fillna(0)
df["DZ"] = df["Z"].diff().fillna(0)
df["DA"] = df["A"].diff().fillna(0)
df.to_csv("data/train_features.csv", index=False)
```

Statistical features: - mean `mean`, 
- standard deviation `std`,
- minimum and maximum `min`,`max`,
- range `max – min`,
- signal energy `sum(x^2)`.

``` python
def extract_features(window):
    features = {}
    for col in ["X", "Y", "Z", "A", "DX", "DY", "DZ", "DA"]:
        data = window[col]
        features[f"{col}_mean"] = data.mean()
        features[f"{col}_std"] = data.std()
        features[f"{col}_min"] = data.min()
        features[f"{col}_max"] = data.max()
        features[f"{col}_range"] = data.max() - data.min()
        features[f"{col}_energy"] = np.sum(data**2)
    features["FALL"] = window["FALL"].max()
    return features
```

### 7.3. ML Models

Tested models: 
- **Random Forest** (200 trees, class balancing),
- **XGBoost** (200 trees, `scale_pos_weight` for imbalanced data).
Final choice: **Random Forest**, providing high accuracy and easier deployment.

### Advantages of ML

-   more robust to unusual movements,
-   model can adapt to new data,
-   fewer false alarms.

## 8. Data Analysis in Jupyter Notebook

### 8.1. Fall detection with manual algorithm
![Manual](Plots/manual.png)
### 8.2. Fall detection with ML model
![Model](Plots/model.png)
### 8.3. Algorithm comparison 
The program `rx_adxl_with_ml.py` was used for comparison, simultaneously applying manual algorithm and ML prediction. In the test signal, two real falls occurred, both **correctly detected** by the ML model.
![Comparison](Plots/modelvsmanual.png)

## 9. Possible Extensions

-   Deploy ML model directly on microcontroller using **STM32Cube.AI**,
-   Add wireless communication (Bluetooth, WiFi) instead of USB,
-   Extend with additional sensors (gyroscope, barometer),
-   Introduce classification of fall types (forward, sideways,
    backward).
