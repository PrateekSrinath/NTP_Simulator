# quick pytest to ensure run_sim returns sane numbers
from src.ntp_simulation import run_sim, load_params

def test_run_sim_basic():
    params = load_params()
    out = run_sim(params)
    assert 'Isp' in out
    assert out['Isp'] > 0
    assert out['thrust'] >= 0
