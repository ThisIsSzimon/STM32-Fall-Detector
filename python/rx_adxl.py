import serial
import csv

ser = serial.Serial('COM6', 115200, timeout=1)

with open('data/nowe_dane.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['X', 'Y', 'Z', 'FALL'])

    try:
        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(line)
                parts = line.split(',')
                if len(parts) == 4:
                    try:
                        x = float(parts[0])
                        y = float(parts[1])
                        z = float(parts[2])
                        fall = int(parts[3])
                        writer.writerow([x, y, z, fall])
                    except ValueError:
                        pass

    except KeyboardInterrupt:
        print("Zakończono odczyt.")
    finally:
        ser.close()

