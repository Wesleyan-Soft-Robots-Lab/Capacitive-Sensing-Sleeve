import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

homedir = os.path.dirname(__file__)
csvPath = os.path.join(homedir, 'standard_dev.csv')
df = pd.read_csv(csvPath)

#legend
plt.plot(-10,-10, marker='o', color='black', label='sensor1')
plt.plot(-10,-10, marker='^', color='black', label='sensor2')
plt.plot(-10,-10, marker='_', color='blue', label='both')
plt.plot(-10,-10, marker='_', color='green', label='short')
plt.plot(-10,-10, marker='_', color='red', label='long')
plt.legend()

test_colors = {
    'both': 'blue',
    'short': 'green',
    'long': 'red',
}

sensor_markers = {
    'sensor1': 'o',
    'sensor2': '^'
}

group = {
    'blue' : 0,
    'green' : 10,
    'red' :20
}

avg_s1 = {
    'both': [],
    'short': [],
    'long': []
    
}
avg_s2 = {
    'both': [],
    'short': [],
    'long': []   
}

for idx, row in df.iterrows():
    test = row['test']
    if test == 0:
        c0 = test_colors['long']
        c1 = test_colors['both']
        avg_s1['long'].append(row['sensor1'])
        avg_s2['both'].append(row['sensor2'])
    elif test == 1:
        c0 = test_colors['short']
        c1 = test_colors['short']
        avg_s1['short'].append(row['sensor1'])
        avg_s2['short'].append(row['sensor2'])
    elif test == 2:
        c0 = test_colors['both']
        c1 = test_colors['long']
        avg_s1['both'].append(row['sensor1'])
        avg_s2['long'].append(row['sensor2'])
    elif test == 3:
        c0 = test_colors['both']
        c1 = test_colors['both']
        avg_s1['both'].append(row['sensor1'])
        avg_s2['both'].append(row['sensor2'])
    elif test == 4:
        c0 = test_colors['long']
        c1 = test_colors['long']
        avg_s1['long'].append(row['sensor1'])
        avg_s2['long'].append(row['sensor2'])

    plt.plot(group[c0],row['sensor1'], marker=sensor_markers['sensor1'], color=c0, fillstyle='none')
    plt.plot(group[c1],row['sensor2'], marker=sensor_markers['sensor2'], color=c1)

plt.ylabel('Sensor Reading (fF)')
plt.title('Sensor Readings by Test and Sensor')
plt.grid(True)

def calcAvg(l):
    count=0
    for x in l:
        count +=x
    return count/len(l)

total_s1 = [0,0,0]
total_s2 = [0,0,0]

for i,k in enumerate(avg_s1.keys()):
    total_s1[i] = calcAvg(avg_s1[k])
for i,k in enumerate(avg_s2.keys()):
    total_s2[i] = calcAvg(avg_s2[k])

print(f"Sensor_1 avgs: Both: {total_s1[0]}\tShort: {total_s1[1]}\tLong: {total_s1[2]}")
print(f"Sensor_2 avgs: Both: {total_s2[0]}\tShort: {total_s2[1]}\tLong: {total_s2[2]}")
plt.show()