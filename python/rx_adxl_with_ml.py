import serial
import csv
import pandas as pd
import numpy as np
from collections import deque
import joblib

# Model ML
rf = joblib.load("models/rf_model.pkl")

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

# Parametry
window_size = 150
buffer = deque(maxlen=window_size)
sample_count = 0
window_index = 0

ser = serial.Serial('COM6', 115200, timeout=1)

with open('data/dane.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['X', 'Y', 'Z', 'FALL_HW', 'FALL_ML'])

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            try:
                x, y, z, fall_hw = map(float, line.split(','))
                fall_hw = int(fall_hw)
            except:
                continue

            A = np.sqrt(x**2 + y**2 + z**2)
            if buffer:
                prev = buffer[-1]
                DX = x - prev["X"]
                DY = y - prev["Y"]
                DZ = z - prev["Z"]
                DA = A - prev["A"]
            else:
                DX = DY = DZ = DA = 0

            buffer.append({"X": x, "Y": y, "Z": z, "A": A,
                           "DX": DX, "DY": DY, "DZ": DZ, "DA": DA,
                           "FALL": fall_hw})
            sample_count += 1

            fall_ml = ""

            # wypisanie próbek z okna
            print(f"X={x:.2f}, Y={y:.2f}, Z={z:.2f}, FALL_HW={fall_hw}")

            # co okno
            if sample_count % window_size == 0:
                window_index += 1
                window_df = pd.DataFrame(buffer)
                feats = extract_features(window_df)
                X_in = pd.DataFrame([feats]).drop("FALL", axis=1)
                fall_ml = int(rf.predict(X_in)[0])

                print("\n--- OKNO #{} ---".format(window_index))
                print({k: round(v, 2) for k, v in feats.items() if k.endswith("_mean") or k=="FALL"})
                print("Predykcja ML:", fall_ml)
                print("---------------\n")

            writer.writerow([x, y, z, fall_hw, fall_ml])

    except KeyboardInterrupt:
        print("Zakończono odczyt.")
    finally:
        ser.close()
