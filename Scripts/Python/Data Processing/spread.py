import numpy as np
import pandas as pd
import plotter as normal
import seaborn as sb
import matplotlib.pyplot as plt

def spread(data_set, id, plot):
    df, max_y, min_y = normal.normalizeData(data_set)
    for col in df.columns:
        if col.isnumeric() and int(col) == id:
            print(f"The standard deviation Of {id}: {df[col].std()}")

    if plot:
        sb.histplot(data=df, x=str(id))
        plt.title(f"Violin Plot of Sensor {id}")
        plt.show()


if __name__ == "__main__":
    MY_CSV_FILE = '/Users/chris/Desktop/Capacitive-Sensing-Sleeve/tests/data/cap-sensor_data/20260710/20260710_1_MOTOR_OFF_8_FDC_2cm_SensorLog.csv'

    spread(MY_CSV_FILE, 0, True)