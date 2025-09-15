# main orchestrator: reads params, runs toy sim, saves a plot
import yaml
import numpy as np
import matplotlib.pyplot as plt

from thermal_1d import generate_toy_power_map, solve_1d_channel
from nozzle import nozzle_isentropic
from utils import R_spec

def load_params(path="src/params.yaml"):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def run_sim(params):
    total_power = params['total_power']
    inlet_T = params['inlet_temperature']
    inlet_P = params['inlet_pressure']
    m_dot = params['mass_flow_guess']
    core_length = params['geometry']['core_length']
    n_slices = params['geometry']['n_slices']
    cp = params['properties']['cp']
    props = {
        'gamma': params['properties']['gamma'],
        'molar_mass': params['properties']['molar_mass']
    }

    power_map, x = generate_toy_power_map(total_power, core_length, n_slices)
    T_gas, T_wall = solve_1d_channel(power_map, m_dot, cp, inlet_T)
    T_stag = T_gas[-1]  # assume chamber stagnation equals outlet gas
    # pressure drop simplified to zero in this toy model; use later real calc
    P_stag = inlet_P

    v_e, Isp, thrust = nozzle_isentropic(T_stag, P_stag, m_dot, props,
                                         Pe=101325.0, Pa=101325.0,
                                         Ae=params['nozzle']['area_exit'])

    # Save a simple plot
    plot_results(x, T_gas, T_wall, Isp, thrust)

    return {
        'T_gas': T_gas.tolist(),
        'T_wall': T_wall.tolist(),
        'Isp': Isp,
        'thrust': thrust
    }

def plot_results(x, T_gas, T_wall, Isp, thrust):
    plt.figure(figsize=(8,4))
    plt.plot(x, T_gas, label='T_gas (K)')
    plt.plot(x, T_wall, label='T_wall (K)')
    plt.xlabel('Axial position (m)')
    plt.ylabel('Temperature (K)')
    plt.title(f'T_gas / T_wall    Isp={Isp:.1f} s  Thrust={thrust:.1f} N')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('figures/T_profile.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    params = load_params()
    out = run_sim(params)
    print("Simulation done:", out)
