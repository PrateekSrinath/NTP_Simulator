# utils.py : constants & helpers
R_universal = 8.314462618
g0 = 9.80665

def R_spec(molar_mass):
    """Specific gas constant (J/kg-K)"""
    return R_universal / molar_mass
