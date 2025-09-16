import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from thermal_1d import generate_toy_power_map, solve_1d_channel
from nozzle import nozzle_isentropic

def load_params(path="src/params.yaml"):
    with open(path, 'r') as f:
        params = yaml.safe_load(f)
    try:
        params['total_power'] = float(params['total_power'])
        params['inlet_temperature'] = float(params['inlet_temperature'])
        params['inlet_pressure'] = float(params['inlet_pressure'])
        params['mass_flow_guess'] = float(params['mass_flow_guess'])
        params['geometry']['core_length'] = float(params['geometry']['core_length'])
        params['geometry']['n_slices'] = int(params['geometry']['n_slices'])
        params['properties']['cp'] = float(params['properties']['cp'])
        params['properties']['gamma'] = float(params['properties']['gamma'])
        params['properties']['molar_mass'] = float(params['properties']['molar_mass'])
        params['properties']['eta_abs'] = float(params['properties']['eta_abs'])
        params['nozzle']['area_throat'] = float(params['nozzle']['area_throat'])
        params['nozzle']['area_exit'] = float(params['nozzle']['area_exit'])
        params['materials']['inconel718_Tmax'] = float(params['materials']['inconel718_Tmax'])
    except (KeyError, TypeError, ValueError) as e:
        raise ValueError(f"Error parsing YAML params: {e}")
    return params

def run_sim(params):
    total_power = params['total_power'] * params['properties']['eta_abs']
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
    T_stag = T_gas[-1]
    P_stag = inlet_P

    v_e, Isp, thrust = nozzle_isentropic(T_stag, P_stag, m_dot, props,
                                        Pe=101325.0, Pa=101325.0,
                                        Ae=params['nozzle']['area_exit'])

    return {
        'x': x.tolist(),
        'T_gas': T_gas.tolist(),
        'T_wall': T_wall.tolist(),
        'Isp': Isp,
        'thrust': thrust,
        'reactor_name': params.get('reactor_name', 'default')
    }

def plot_results(x, T_gas, T_wall, Isp, thrust, reactor_name='default'):
    plt.figure(figsize=(8,4))
    plt.plot(x, T_gas, label='T_gas (K)')
    plt.plot(x, T_wall, label='T_wall (K)')
    plt.xlabel('Axial position (m)')
    plt.ylabel('Temperature (K)')
    plt.title(f'{reactor_name}: T_gas / T_wall | Isp={Isp:.1f} s | Thrust={thrust:.1f} N')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'figures/{reactor_name}_T_profile.png', dpi=300)
    plt.close()

def run_batch_sim(csv_path="data/reactors.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file {csv_path} not found.")
    
    results = []
    for idx, row in df.iterrows():
        params = {
            'reactor_name': row['reactor_name'],
            'total_power': float(row['total_power_MW']) * 1e6,
            'inlet_temperature': float(row['inlet_temperature_K']),
            'inlet_pressure': float(row['inlet_pressure_Pa']),
            'mass_flow_guess': float(row['mass_flow_kg_s']),
            'geometry': {
                'core_length': float(row['core_length_m']),
                'n_slices': int(row['n_slices'])
            },
            'nozzle': {
                'area_throat': float(row['area_throat_m2']),
                'area_exit': float(row['area_exit_m2'])
            },
            'materials': {
                'inconel718_Tmax': float(row['inconel718_Tmax_K'])
            },
            'properties': {
                'cp': float(row['cp_J_kg_K']),
                'gamma': float(row['gamma']),
                'molar_mass': float(row['molar_mass_kg_mol']),
                'eta_abs': float(row['eta_abs'])
            }
        }
        out = run_sim(params)
        plot_results(out['x'], out['T_gas'], out['T_wall'], out['Isp'], out['thrust'], out['reactor_name'])
        results.append(out)

    plt.figure(figsize=(10,6))
    for res in results:
        plt.plot(res['x'], res['T_gas'], label=f"{res['reactor_name']} (Isp={res['Isp']:.1f} s)")
    plt.xlabel('Axial position (m)')
    plt.ylabel('Gas Temperature (K)')
    plt.title('Gas Temperature Profiles Across Reactors')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('figures/comparison_T_gas.png', dpi=300)
    plt.close()

    summary_df = pd.DataFrame([
        {'reactor_name': res['reactor_name'], 'Isp': res['Isp'], 'thrust': res['thrust']}
        for res in results
    ])
    summary_df.to_csv('data/simulation_results.csv', index=False)
    return results

if __name__ == "__main__":
    params = load_params()
    out = run_sim(params)
    print("Single simulation done:", out)
