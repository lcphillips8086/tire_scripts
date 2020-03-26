import sys
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from segmentation import *

def sweep_average(data, sweep, segments):
    summation = 0.0 
    for index in sweep:
        segment = segments[index]
        summation += np.mean(data[segment[0]:segment[1]])

    return summation / len(sweep)

def scan_directory(directory):
    files = glob.glob("%s/*.dat" % directory)
    file_dict = dict()
    for path in files:
        name = os.path.split(path)[1]
        project = int(name[1:5])
        run = int(name[8:-4])
        file_dict[(project, run)] = path
    return file_dict

def main():
    if len(sys.argv) != 3:
        print "Wrong number of arguments."
        print "Usage: python2 tire.py <database> <data directory>"
        return

    conn = sqlite3.connect(sys.argv[1])
    file_dict = scan_directory(sys.argv[2])

    c = conn.cursor()

    c.execute("SELECT PROJECT,RUN,TYPE FROM runs WHERE TYPE='lateral' OR TYPE='combined'")
    runs = c.fetchall()

    for run in runs:
        filename = file_dict.get(run[0:2])
        if filename == None:
            print "Warning: Data file for project %d run %d not found." % run[0:2]
            continue

        data = read_tire_data(filename)
        if run[2] == 'lateral':
            segments, sweeps = segment_cornering(data)
            print "Lateral %s: %d sweeps" % (filename, len(sweeps))
        if run[2] == 'combined':
            segments, sweeps = segment_combined(data)
            print "Combined %s: %d sweeps" % (filename, len(sweeps))
        lengths = [segment[1] - segment[0] for segment in segments]
        lengths.sort(reverse=True)
        print "Longest segment: %d steps" % lengths[0]

    return

    data = read_tire_data(sys.argv[1])
    segments, sweeps = segment_cornering(data)

    for idx, sweep in enumerate(sweeps):
        average_pressure = sweep_average(data['P'], sweep, segments)
        average_camber = sweep_average(data['IA'], sweep, segments)
        average_fz = sweep_average(data['FZ'], sweep, segments)
        average_speed = sweep_average(data['V'], sweep, segments)
        psi = np.round(0.145 * average_pressure)
        ia = np.round(average_camber)
        lbs = -10 * np.round(0.2248 * average_fz / 10)
        mph = np.round(average_speed * (1000 * 100 / 2.54 / 12 / 5280))

        print "Sweep %d:" % (idx,)
        print "%dpsi, %ddeg, %dlbs, %dmph" % (psi, ia, lbs, mph)
       
    return

    time = data['ET']
    slip = data['SA']
    force = data['FY']

    plt.subplots_adjust(hspace=0.4)
    ax1 = plt.subplot(4,1,1)
    ax1.set_title('Fz')
    ax1.plot(time, data['FZ'], '-')
    ax2 = plt.subplot(4,1,2, sharex=ax1)
    ax2.set_title('Inclination Angle')
    ax2.plot(time, data['IA'], '-')
    ax3 = plt.subplot(4,1,3, sharex=ax1)
    ax3.set_title('Pressure')
    ax3.plot(time, data['P'], '.')
    ax4 = plt.subplot(4,1,4, sharex=ax1)
    ax4.set_title('Slip Angle')
    ax4.plot(time, slip, '-')
    for x1, x2 in segments:
        ax4.plot((time[x1], time[x2]), (slip[x1], slip[x2]), '.')

    plt.ion()
    plt.show()

    raw_input("Press enter to continue.")

if __name__ == "__main__":
    main()
