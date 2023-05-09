import itertools
import math

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from matplotlib.collections import LineCollection, CircleCollection, PatchCollection, PolyCollection


def mirrored_interval(step: float, n: int):
    array = np.arange(0, n * step, step)
    return array - (array[-1] / 2)


def main():
    st.title("Side-scan resolution calculator")
    ground_range, vessel_speed, beam_width = get_input()
    sound_velocity = 1500
    n_sensor_positions = 5
    altitude_percentage = 10
    altitude = altitude_percentage / 100 * ground_range
    hypothenusa = math.sqrt(altitude ** 2 + ground_range ** 2)

    ping_rate = sound_velocity / (2 * hypothenusa)
    ping_interval = vessel_speed / ping_rate
    sensor_y = mirrored_interval(ping_interval, n_sensor_positions)
    centers = [np.array([0, y]) for y in sensor_y]
    beam_width_m = math.tan(math.radians(beam_width)) * ground_range
    right_polygons = [Polygon([(0, y), (ground_range, y + beam_width_m), (ground_range, y - beam_width_m)],
                              alpha=0.2) for y in sensor_y]
    left_polygons = [Polygon([(0, y), (-ground_range, y + beam_width_m), (-ground_range, y - beam_width_m)],
                             alpha=0.2) for y in sensor_y]
    fig, ax = plt.subplots()
    for p in right_polygons:
        ax.add_patch(p)
    for p in left_polygons:
        ax.add_patch(p)
    ax.scatter(*np.array(centers).T)
    ax.axis([-10, ground_range+10, -1, 1])

    ax.axvline(x=0, color='r', linestyle='--', label='Track')

    ax.set_xlabel("Cross-track [m]")
    ax.set_ylabel("Along-track [m]")
    # ax.set_title("Detection Range")
    # ax.set_aspect('equal')
    st.pyplot(fig)
    resolution = beam_width_m * 2 * 0.9
    if ping_interval > resolution:
        st.text(f'Along-track resolution is limited by ping interval.')
        st.text(f'Resolution by ping interval: {ping_interval:.2g}')
    else:
        st.text(f'Along-track resolution at 90% of range: {resolution :.2g} m')

def get_input():
    range = st.slider("(ground) Range (per channel) [m]", 0.0, 200.0, 70.0, step=0.5)
    speed = st.slider("Vessel speed [m/s]", 0.0, 10.0, 3.0, step=0.1)
    beam_width = st.slider("Beam width [degrees]", 0.0, 2.0, 0.28, step=0.01)
    return range, speed, beam_width


if __name__ == '__main__':
    main()
