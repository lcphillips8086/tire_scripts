import numpy as np
import bisect as bi
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
from scipy.signal import argrelextrema

def read_tire_data(filename):
    fd = open(filename)
    _ = fd.readline()
    column_names = fd.readline().split()
    ndtype = list(((i, np.double) for i in column_names))
    _ = fd.readline()
    data = np.genfromtxt(fd, dtype=ndtype)
    fd.close()
    return data

def segment_combined(data):
    time = data['ET']
    slip = data['SR']

    gauss = gaussian_filter1d(slip, sigma=10, order=0)
    maxima = argrelextrema(gauss, np.greater, order=4)[0]
    minima = argrelextrema(gauss, np.less, order=4)[0]

    max_condition = np.greater(slip[maxima], 0.05)
    min_condition = np.less(slip[minima], -0.12)
    maxima = np.extract(max_condition, maxima).copy()
    minima = np.extract(min_condition, minima).copy()

    maxima.sort()
    minima.sort()

    segments = []
    sweeps = []

    for minimum in minima:
        maximum_idx = bi.bisect(maxima, minimum);
        if maximum_idx == len(maxima):
            maximum_after = len(gauss) - 1
        else:
            maximum_after = maxima[maximum_idx]

        maximum_before = maxima[maximum_idx - 1]

        idx = minimum

        while gauss[idx] < 0.9 * gauss[minimum]:
            idx -= 1
        end_one = idx
        while gauss[idx] < 0.9 * gauss[maximum_before] and \
              time[idx] - time[idx - 1] < 0.1:
            idx -= 1
        start_one = idx

        idx = minimum

        while gauss[idx] < 0.9 * gauss[minimum]:
            idx += 1
        start_two = idx
        while gauss[idx] < 0.9 * gauss[maximum_after] and \
              (idx + 1) < len(gauss) and \
              time[idx + 1] - time[idx] < 0.1:
            idx += 1
        end_two = idx

        # limit the length of either segment in a sweep. this filters out a
        # common error in segmenting combined sweeps from Calspan data
        if ((end_one - start_one) < 1000 and (end_two - start_two) < 1000):
            segments.append((start_one, end_one))
            segments.append((start_two, end_two))
            sweeps.append((len(segments) - 2, len(segments) - 1))

    return segments, sweeps

def segment_cornering(data):
    slip = data['SA']
    time = data['ET']

    gauss = gaussian_filter1d(slip, sigma=4, order=0)
    maxima = argrelextrema(gauss, np.greater)[0]
    minima = argrelextrema(gauss, np.less)[0]

    max_condition = np.greater(slip[maxima], 10.0)
    min_condition = np.less(slip[minima], -10.0)
    maxima = np.extract(max_condition, maxima)
    minima = np.extract(min_condition, minima)
    max_condition = np.full(maxima.size, False)
    min_condition = np.full(minima.size, False)

    for idx, maximum in enumerate(maxima):
        max_condition[idx] = (idx == 0 or (time[maximum] - time[maxima[idx - 1]]) > 10.0) and \
                             (idx == (maxima.size-1) or (time[maxima[idx + 1]] - time[maximum]) > 10.0)

    for idx, minimum in enumerate(minima):
        min_condition[idx] = (idx == 0 or (time[minimum] - time[minima[idx - 1]]) > 10.0) and \
                             (idx == (minima.size-1) or (time[minima[idx + 1]] - time[minimum]) > 10.0)

    maxima = np.extract(max_condition, maxima).copy()
    minima = np.extract(min_condition, minima).copy()
    maxima.sort()
    minima.sort()
    extrema = list(zip(maxima, minima))

    segments = []
    sweeps = []

    for maximum, minimum in extrema:
        idx = maximum

        while gauss[idx] > 0.9 * gauss[maximum]:
            idx -= 1
        end = idx
        while gauss[idx] > 0:
            idx -= 1
        start = idx

        segments.append((start, end))
        
        idx = maximum

        while gauss[idx] > 0.9 * gauss[maximum]:
            idx += 1
        start = idx
        while gauss[idx] > 0.9 * gauss[minimum]:
            idx += 1
        end = idx

        segments.append((start, end))

        idx = minimum

        while gauss[idx] < 0.9 * gauss[minimum]:
            idx += 1
        start = idx
        while idx < len(gauss)-1 and gauss[idx] < 0:
            idx += 1
        end = idx

        segments.append((start, end))
        sweeps.append((len(segments) - 3, len(segments) - 2, len(segments) - 1))

    return segments, sweeps
