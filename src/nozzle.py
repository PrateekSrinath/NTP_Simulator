
import math
from utils import g0, R_spec

def nozzle_isentropic(T0, P0, m_dot, props, Pe=101325.0, Pa=101325.0, Ae=None):
    """
    Calculate ideal isentropic nozzle performance.
    
    Args:
        T0: stagnation temperature (K) - must be > 0
        P0: stagnation pressure (Pa) - must be > 0
        m_dot: mass flow rate (kg/s) - must be > 0
        props: dict with 'gamma' (specific heat ratio > 1) and 'molar_mass' (kg/mol > 0)
        Pe: exit pressure (Pa) - must be <= P0 for meaningful results
        Pa: ambient pressure (Pa) - defaults to sea level
        Ae: exit area (m²) - optional for pressure thrust correction
        
    Returns:
        tuple: (v_e, Isp, thrust) where:
            v_e: exit velocity (m/s)
            Isp: specific impulse (s)
            thrust: total thrust (N)
            
    Notes:
        - For Pe >= P0, returns zero values (no flow condition)
        - Assumes isentropic expansion to specified exit pressure
        - Pressure thrust added only if Ae is provided
    """
    if T0 <= 0 or P0 <= 0 or m_dot <= 0:
        return 0.0, 0.0, 0.0
    
    gamma = props.get('gamma', 1.35)
    M_molar = props.get('molar_mass', 0.002)
    
    if gamma <= 1.0 or M_molar <= 0:
        return 0.0, 0.0, 0.0

    if Pe >= P0:
        return 0.0, 0.0, 0.0
    
    R = R_spec(M_molar)
    
    term = 1.0 - (Pe / P0) ** ((gamma - 1.0) / gamma)
    factor = 2.0 * gamma / (gamma - 1.0)
    v_e = math.sqrt(factor * R * T0 * term)

    Isp = v_e / g0
    thrust = m_dot * v_e
    
    if Ae is not None and Ae > 0:
        thrust += (Pe - Pa) * Ae
    
    return v_e, Isp, thrust

def nozzle_isentropic_enhanced(T0, P0, m_dot, props, Pe=101325.0, Pa=101325.0, Ae=None):
    """
    Enhanced isentropic nozzle model with additional diagnostics.
    
    Returns additional information about flow conditions.
    """
   
    v_e, Isp, thrust = nozzle_isentropic(T0, P0, m_dot, props, Pe, Pa, Ae)
    
    if v_e == 0:  
        return {
            'v_e': 0.0,
            'Isp': 0.0,
            'thrust': 0.0,
            'status': 'no_flow',
            'is_choked': False,
            'P_crit': None,
            'M_e': 0.0
        }
    
    gamma = props.get('gamma', 1.35)
    M_molar = props.get('molar_mass', 0.002)
    R = R_spec(M_molar)
    
    
    P_crit_ratio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
    P_crit = P0 * P_crit_ratio
    is_choked = Pe <= P_crit
    
    
    T_e = T0 * (Pe / P0) ** ((gamma - 1.0) / gamma)
    a_e = math.sqrt(gamma * R * T_e)  # Speed of sound at exit
    M_e = v_e / a_e if a_e > 0 else 0.0
    
    return {
        'v_e': v_e,
        'Isp': Isp,
        'thrust': thrust,
        'status': 'choked' if is_choked else 'unchoked',
        'is_choked': is_choked,
        'P_crit': P_crit,
        'M_e': M_e,
        'T_e': T_e,
        'a_e': a_e
    }
