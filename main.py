import itertools
import math

import pandas as pd
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from matplotlib.collections import LineCollection, CircleCollection, PatchCollection, PolyCollection


# resolution_from_manual [range, nominal_frequency]
resolution_from_manual = {'EdgeTech 4200-MP': {
    100:  (200, 5),
    300: (150, 1.3),
    400: (100, 0.6),
    600: (100, 0.45),
    900:  (50, 0.18),
}}


def mirrored_interval(step: float, n: int):
    array = np.arange(0, n * step, step)
    return array - (array[-1] / 2)


def main():
    st.title("Side-scan resolution calculator")
    ground_range, vessel_speed, beam_width, frequency, mode, instrument = get_input()
    sound_velocity = 1500
    n_sensor_positions = 7
    altitude_percentage = 10
    altitude = altitude_percentage / 100 * ground_range
    hypothenusa = math.sqrt(altitude ** 2 + ground_range ** 2)
    if mode == 'HSM':
        ping_rate = sound_velocity / (2 * hypothenusa) * 2
    elif mode == 'HDM':
        ping_rate = sound_velocity / (2 * hypothenusa)

    ping_interval = vessel_speed / ping_rate
    sensor_y = mirrored_interval(ping_interval, n_sensor_positions)
    centers = [np.array([0, y]) for y in sensor_y]
    beam_width_m = math.tan(math.radians(beam_width)) * ground_range
    array_length = 0.4  # [m]
    nearfield_range = array_length ** 2 / (4 * sound_velocity / frequency / 1000)  # D**2
    # D: length
    # F: frequency
    # C: sound velocity
    nadir_range = 2
    v = 0.5 * array_length
    right_polygons = [Polygon(
        [(nearfield_range, y - v), (nadir_range, y - v), (nadir_range, y + v), (nearfield_range, y + v),
         (ground_range, y + beam_width_m), (ground_range, y - beam_width_m)],
        alpha=0.2) for y in sensor_y]
    left_polygons = [Polygon([(0, y), (-ground_range, y + beam_width_m), (-ground_range, y - beam_width_m)],
                             alpha=0.2) for y in sensor_y]
    fig, ax = plt.subplots()
    for p in right_polygons:
        ax.add_patch(p)
    for p in left_polygons:
        ax.add_patch(p)
    ax.scatter(*np.array(centers).T, label=f'Ping interval ({ping_interval:.2f} m)')
    # ax.axis([-10, ground_range + 10, -1, 1])
    ax.axis([-10, 120, -1, 1])
    ax.axvline(x=0, color='r', linestyle='--', label='Sensor track')
    ax.axvline(x=nearfield_range, color='blue', linewidth=0.4, linestyle='--', label='Near<->far field transition')
    ax.axvline(x=nadir_range, color='brown', linewidth=0.4, linestyle='--', label='Nadir')

    ax.set_xlabel("Cross-track distance [m]")
    ax.set_ylabel("Along-track [m]")
    # ax.set_title("Detection Range")
    # ax.set_aspect('equal')
    ax.legend()
    st.pyplot(fig)
    resolution = beam_width_m * 2
    if ping_interval > resolution:
        st.text(f'Along-track resolution is limited by ping interval.')
        st.text(f'Resolution by ping interval: {ping_interval:.2g}')
    else:
        st.text(f'Along-track resolution at 90% of range: {resolution * 0.9 :.2g} m')

    fig2, ax2 = plt.subplots()
    lc = LineCollection([[(0, v), (nearfield_range, v), (ground_range, resolution)]], linewidth=3.0, )
    ax2.axis([0, ground_range + 10, 0, resolution * 1.1])
    ax2.add_collection(lc)
    v = resolution_from_manual.get(instrument).get(frequency)
    if v:
        ax2.scatter([v[0]], [v[1]], label='According to Edgetech manual')
    ax2.set_title("Resolution over distance")
    ax2.legend()
    ax2.set_xlabel("Cross-track distance [m]")
    ax2.set_ylabel("Across track resolution [m]")
    st.pyplot(fig2)


def get_input():
    range = st.slider("(ground) Range (per channel) [m]", 10.0, 200.0, 70.0, step=0.5)
    speed = st.slider("Vessel speed [m/s]", 0.0, 10.0, 3.0, step=0.1)

    data = {'EdgeTech 4200-MP': {'HDM': {100: 0.64, 300: 0.28, 400: 0.3, 600: 0.26, 900: 0.2},
                                 'HSM': {100: 1.26, 300: 0.54, 400: 0.4, 600: 0.34, 900: 0.3}
                                 },
            'Edgetech 4125': {'HDM': {400: 0.46, 600: 0.33, 900: 0.28, 1600: 0.2}},
            'Edgetech 4205': {'HDM': {120: 0.7, 230: 0.44, 410: 0.28, 540: 0.26, 850: 0.23},
                              'HSM': {120: 0.95, 230: 0.63, 410: 0.38, 540: 0.35, 850: 0.3}},
            }
    instrument = st.sidebar.selectbox("Instrument", data.keys())
    mode = st.sidebar.selectbox("Mode", data[instrument])
    freq = st.sidebar.selectbox("Frequency", data[instrument][mode])
    beam_width = data[instrument][mode][freq]
    st.sidebar.text(f"Beamwidth of chosen configuration: \n{beam_width:.2f}°")

    st.sidebar.text(f"data from :\n"
                    f"https://www.edgetech.com/wp-content/uploads/2019/07/0004842_Rev_P.pdf")

    st.sidebar.text(f"sources from https://www.edgetech.com/resource-center/: \n"
                    f"https://www.edgetech.com/wp-content/uploads/2019/07/app_note_beamwidth.pdf \n"
                    f"https://www.edgetech.com/wp-content/uploads/2020/10/Feature-detection-Rev3.pdf")
    return range, speed, beam_width, freq, mode, instrument


if __name__ == '__main__':
    main()
