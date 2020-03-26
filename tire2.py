import sys
import numpy as np
import matplotlib.pyplot as plt
from segmentation import *

def main():
    if len(sys.argv) != 2:
        print "Wrong number of arguments."
        print "Usage: python2 tire.py <data>"
        return

    data = read_tire_data(sys.argv[1])
    segments, sweeps = segment_combined(data)

    time = data['ET']
    slip = data['SR']
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
    ax4.set_title('Slip')
    ax4.plot(time, slip, '-')
    for x1, x2 in segments:
        ax4.plot((time[x1], time[x2]), (slip[x1], slip[x2]), '.')

    plt.ion()
    plt.show()

    raw_input("Press enter to continue.")

if __name__ == "__main__":
    main()
