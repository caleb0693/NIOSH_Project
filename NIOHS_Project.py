import pandas as pd
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import plotly.express as px
import streamlit as st
import time


sensor_data = pd.read_csv("October31.csv")
sensor_data["Timestamp"] = pd.to_datetime(sensor_data["Date"] + " " + sensor_data["Time"])
sensor_data = sensor_data.drop(columns=["Date", "Time"])

st.title("NIOSH Sensor Data Visualization Project")
st.write("Created by Caleb Ginorio González, CIH, CSP")

img = Image.open("niosh_sensor.png")
img_width, img_height = img.size


fig = px.imshow(np.asarray(img))
fig.update_layout(
    dragmode="pan",
    height=700,
    width=700,
    title="Hover over the image to get coordinates",
    xaxis=dict(showgrid=False, zeroline=False),
    yaxis=dict(showgrid=False, zeroline=False),
)
hover_data = st.plotly_chart(fig, use_container_width=True)

st.sidebar.write("### Enter Coordinates for Each Sensor:")
sensor_labels = ["AboveSuperSac", "ControlRoom", "Palletizer", "TransferPoint", "TruckLoading"]

sensor_coordinates = {}
for label in sensor_labels:
    st.sidebar.write(f"**{label}**")
    x = st.sidebar.number_input(f"X Coordinate for {label}:", min_value=0, max_value=img_width - 1, key=f"{label}_x")
    y = st.sidebar.number_input(f"Y Coordinate for {label}:", min_value=0, max_value=img_height - 1, key=f"{label}_y")
    sensor_coordinates[label] = (x, y)


st.write("### Select Time Range for Animation")
start_time, end_time = st.slider(
    "Select the time range:",
    min_value=sensor_data["Timestamp"].min().to_pydatetime(),
    max_value=sensor_data["Timestamp"].max().to_pydatetime(),
    value=(sensor_data["Timestamp"].min().to_pydatetime(), sensor_data["Timestamp"].max().to_pydatetime()),
    format="MM/DD HH:mm",
)


if st.button("Play for Animation"):
    melted_data = sensor_data.melt(id_vars=["Timestamp"], var_name="SensorID", value_name="Value")
    global_min = melted_data["Value"].min()
    global_max = melted_data["Value"].max()

    animation_placeholder = st.empty()

    time_range = melted_data[(melted_data["Timestamp"] >= pd.Timestamp(start_time)) & (melted_data["Timestamp"] <= pd.Timestamp(end_time))]["Timestamp"].unique()

    for current_time in time_range:
        filtered_data = melted_data[melted_data["Timestamp"] == current_time]

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(img, alpha=0.6)

        for _, row in filtered_data.iterrows():
            sensor_id = row["SensorID"]
            x, y = sensor_coordinates[sensor_id]
            value = row["Value"]

            circle_size = max(50, value * 2)  # Minimum size of 50, scales with value

            ax.scatter(x, y, c=[value], cmap="plasma", norm=Normalize(vmin=global_min, vmax=global_max), s=circle_size, edgecolors="black")

            ax.text(x + 40, y, f"{value:.1f}", color="black", ha="left", va="center", fontsize=8)

        ax.axis('off')
        ax.set_title(f"Sensor Data - {current_time}")

        sm = plt.cm.ScalarMappable(cmap="plasma", norm=Normalize(vmin=global_min, vmax=global_max))
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.046, pad=0.04)
        cbar.set_label('Sensor Value', fontsize=12)

        animation_placeholder.pyplot(fig)
        time.sleep(0.5)
