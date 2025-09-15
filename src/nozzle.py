# nozzle.py: ideal isentropic nozzle model (toy)
import math
from utils import g0, R_spec

def nozzle_isentropic(T0, P0, m_dot, props, Pe=101325.0, Pa=101325.0, Ae=None):
    """
    T0: stagnation temperature (K)
    P0: stagnation pressure (Pa)
    m_dot: mass flow (kg/s)
    props: dict with gamma and molar_mass
    Returns (v_e, Isp, thrust)
    """
    gamma = props.get('gamma', 1.35)
    M_molar = props.get('molar_mass', 0.002)
    R = R_spec(M_molar)
    # safety clamp if Pe >= P0 -> v_e = 0
    if Pe >= P0:
        return 0.0, 0.0, 0.0
    term = 1.0 - (Pe / P0) ** ((gamma - 1.0) / gamma)
    factor = 2.0 * gamma / (gamma - 1.0)
    v_e = math.sqrt(factor * R * T0 * term)
    Isp = v_e / g0
    thrust = m_dot * v_e
    # add pressure thrust if area_exit (Ae) provided
    if Ae is not None:
        thrust += (Pe - Pa) * Ae
    return v_e, Isp, thrust