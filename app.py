import sys, os
import streamlit as st
import matplotlib.pyplot as plt

# --- Fix path so we can import from src/ ---
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from ntp_simulation import run_sim  # now works!

# --- Streamlit App ---
st.title("🚀 Nuclear Thermal Propulsion Prototype")

st.markdown(
    "Adjust the sliders to explore how reactor parameters affect performance "
    "(Isp & Thrust) and gas/wall temperature profiles."
)

# --- Sliders for user input ---
power = st.slider("Reactor Power (MW)", 100, 2000, 500, step=100)
mass_flow = st.slider("Mass Flow (kg/s)", 5, 50, 15, step=1)
area_exit = st.slider("Nozzle Exit Area (m²)", 0.005, 0.05, 0.01, step=0.005)

# --- Build params dict ---
params = {
    "reactor_name": "Streamlit_Reactor",
    "total_power": power * 1e6,        # convert MW -> W
    "inlet_temperature": 300,          # K
    "inlet_pressure": 3e6,             # Pa
    "mass_flow_guess": mass_flow,      # kg/s
    "geometry": {"core_length": 1.2, "n_slices": 100},
    "nozzle": {"area_throat": 0.001, "area_exit": area_exit},
    "materials": {"inconel718_Tmax": 1000},
    "properties": {
        "cp": 14000,
        "gamma": 1.35,
        "molar_mass": 0.002,
        "eta_abs": 1.0,
    },
}

# --- Run simulation ---
out = run_sim(params)

# --- Display performance numbers ---
st.subheader("Performance Results")
st.write(f"**Isp:** {out['Isp']:.1f} s")
st.write(f"**Thrust:** {out['thrust']:.1f} N")

# --- Plot temperature profile ---
fig, ax = plt.subplots(figsize=(7,4))
ax.plot(out["x"], out["T_gas"], label="Gas Temp (K)")
ax.plot(out["x"], out["T_wall"], label="Wall Temp (K)")
ax.set_xlabel("Axial position (m)")
ax.set_ylabel("Temperature (K)")
ax.set_title(f"Temperature Profile — {out['reactor_name']}")
ax.legend()
ax.grid(True)
st.pyplot(fig)
