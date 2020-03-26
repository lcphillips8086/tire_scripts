import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from segmentation import *


def main():
    if len(sys.argv) != 2:
        print "Wrong number of arguments.\n"
        return

    data = read_tire_data(sys.argv[1])
    segments, sweeps = segment_cornering(data)
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

    fig, ax = plt.subplots()
    axrelax = plt.axes([0.2, 0.02, 0.65, 0.03])

    relax = 0
    sweep = sweeps[0]
    seg = segments[sweep[0]]
    line0, = ax.plot(slip[seg[0]:seg[1]], force[(seg[0]+relax):(seg[1]+relax)], '.', label='0')
    seg = segments[sweep[1]]
    line1, = ax.plot(slip[seg[0]:seg[1]], force[(seg[0]+relax):(seg[1]+relax)], '.', label='1')
    seg = segments[sweep[2]]
    line2, = ax.plot(slip[seg[0]:seg[1]], force[(seg[0]+relax):(seg[1]+relax)], '.', label='2')
    ax.legend()

    srelax = Slider(axrelax, 'Relaxation Steps', -10, 10, 0)
    
    def update(val):
        relax = int(srelax.val)
        seg = segments[sweep[0]]
        line0.set_ydata(force[(seg[0]+relax):(seg[1]+relax)])
        seg = segments[sweep[1]]
        line1.set_ydata(force[(seg[0]+relax):(seg[1]+relax)])
        seg = segments[sweep[2]]
        line2.set_ydata(force[(seg[0]+relax):(seg[1]+relax)])
        fig.canvas.draw()
        fig.canvas.flush_events()

    srelax.on_changed(update)

    plt.ion()
    plt.show()

    raw_input("Press enter to continue.")

if __name__ == "__main__":
    main()
