# simple 1D channel thermal solver
import numpy as np

def generate_toy_power_map(total_power, core_length, n_slices):
    """
    Make a simple axial (Gaussian) power distribution normalized to total_power.
    Returns q_i (W per slice) array length n_slices.
    """
    x = np.linspace(0, core_length, n_slices)
    # center-peaked Gaussian
    center = core_length / 2.0
    sigma = core_length / 5.0
    profile = np.exp(-0.5 * ((x - center)/sigma)**2)
    profile /= profile.sum()
    q = profile * total_power
    return q, x

def solve_1d_channel(power_map, mass_flow, cp, inlet_T):
    """
    Very simple steady integration:
      m_dot * cp * dT/dx = q'(x) (power per slice)
    power_map: W per slice (array)
    Returns: T_gas_profile (K array), T_wall_estimate (simple offset)
    """
    n = len(power_map)
    T = np.zeros(n)
    T_wall = np.zeros(n)
    T_prev = inlet_T
    for i in range(n):
        q_slice = power_map[i]  # W (for slice)
        # assume slice length normalized => use energy balance per slice
        dT = q_slice / (mass_flow * cp)
        T_i = T_prev + dT
        # crude wall estimate: assume wall is hotter than gas by small delta
        # (in real model compute convective h => q'' = h*(T_wall - T_gas))
        T_wall_i = T_i + 50.0  # +50 K crude offset; later replace with convective calc
        T[i] = T_i
        T_wall[i] = T_wall_i
        T_prev = T_i
    return T, T_wall
