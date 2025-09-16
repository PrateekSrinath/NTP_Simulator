import numpy as np

def generate_toy_power_map(total_power, core_length, n_slices):
    x = np.linspace(0, core_length, n_slices)
    profile = np.linspace(0.1, 1.0, n_slices, dtype=float)
    q = profile * total_power
    return q, x

def solve_1d_channel(power_map, mass_flow, cp, inlet_T):
    n = len(power_map)
    T = np.zeros(n)
    T_wall = np.zeros(n)
    T_prev = inlet_T
    for i in range(n):
        q_slice = power_map[i]
        dT = q_slice / (mass_flow * cp)
        T_i = T_prev + dT
        T_wall_i = T_i + 50.0
        T[i] = T_i
        T_wall[i] = T_wall_i
        T_prev = T_i
    return T, T_wall
