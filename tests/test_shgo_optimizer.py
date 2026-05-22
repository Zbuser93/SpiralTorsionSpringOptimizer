import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from spiral_torsion_spring_optimizer import SpiralTorsionSpring
from tests.cases import CASES, FEASIBLE_CASES, INFEASIBLE_CASES

CONS_TOL = 1e-2  # matches the round(c, 2) check inside maximize_stiffness


@pytest.fixture(scope="module")
def solved():
    """Run SHGO once per feasible case; share results across tests."""
    return {
        name: SpiralTorsionSpring.maximize_stiffness(inp)
        for name, inp in FEASIBLE_CASES.items()
    }


# --- group 1: feasible cases succeed --------------------------------------

@pytest.mark.parametrize("name", list(FEASIBLE_CASES))
def test_feasible_case_succeeds(solved, name):
    sp = solved[name]
    assert sp.res.success is True, f"{name}: {sp.res.message}"
    assert sp.stiffness > 0
    assert sp.thickness > 0
    assert sp.arclength_E > 0


# --- group 2: infeasible cases raise ValueError ---------------------------

@pytest.mark.parametrize("name", list(INFEASIBLE_CASES))
def test_infeasible_case_raises(name):
    inp = INFEASIBLE_CASES[name]
    with pytest.raises(ValueError):
        SpiralTorsionSpring.maximize_stiffness(inp)


# --- group 3: constraints satisfied ---------------------------------------

@pytest.mark.parametrize("name", list(FEASIBLE_CASES))
def test_constraints_satisfied(solved, name):
    sp = solved[name]
    assert sp.c1 >= -CONS_TOL, f"stress constraint violated: c1={sp.c1}"
    assert sp.c2 >= -CONS_TOL, f"min-radius constraint violated: c2={sp.c2}"
    assert sp.c3 >= -CONS_TOL, f"max-radius constraint violated: c3={sp.c3}"


# --- group 4: geometric consistency ---------------------------------------

@pytest.mark.parametrize("name", list(FEASIBLE_CASES))
def test_geometric_consistency(solved, name):
    sp = solved[name]
    inp = FEASIBLE_CASES[name]
    assert sp.radius_E - CONS_TOL <= sp.radius_pre <= inp['max_radius_pre'] + CONS_TOL
    t_lo, t_hi = sp.thickness_bounds
    l_lo, l_hi = sp.arclength_bounds
    assert t_lo - 1e-9 <= sp.thickness <= t_hi + 1e-9
    assert l_lo - 1e-6 <= sp.arclength_E <= l_hi + 1e-6
    assert sp.number_revolutions > 0


# --- group 5: stiffness formula self-consistency --------------------------

@pytest.mark.parametrize("name", list(FEASIBLE_CASES))
def test_stiffness_formula(solved, name):
    sp = solved[name]
    inp = FEASIBLE_CASES[name]
    expected = inp['elasticity'] * inp['height'] * sp.thickness ** 3 / (12 * sp.arclength_E)
    assert sp.stiffness == pytest.approx(expected, rel=1e-9)


# --- group 6: determinism -------------------------------------------------

def test_determinism_default_sobol():
    inp = FEASIBLE_CASES["readme"]
    a = SpiralTorsionSpring.maximize_stiffness(inp)
    b = SpiralTorsionSpring.maximize_stiffness(inp)
    assert a.thickness == b.thickness
    assert a.arclength_E == b.arclength_E
    assert a.stiffness == b.stiffness


# --- group 7: bound activations -------------------------------------------

def test_max_thickness_binds(solved):
    sp = solved["max_thickness_binds"]
    inp = FEASIBLE_CASES["max_thickness_binds"]
    assert sp.thickness == pytest.approx(inp['max_thickness'], abs=1e-3)


def test_max_radius_binds(solved):
    sp = solved["max_radius_binds"]
    # c3 (max-radius slack) should be the smallest of the three constraints
    assert sp.c3 <= sp.c1 + 1e-2
    assert sp.c3 <= sp.c2 + 1e-2
    assert sp.c3 == pytest.approx(0.0, abs=1e-2)


# --- group 8: min_thickness override --------------------------------------

def test_min_thickness_raises_lower_bound(solved):
    sp = solved["min_thickness_raised"]
    inp = FEASIBLE_CASES["min_thickness_raised"]
    assert sp.thickness_bounds[0] >= inp['min_thickness'] - 1e-9
    assert sp.thickness >= inp['min_thickness'] - CONS_TOL


# --- group 9: opt_params plumbing -----------------------------------------

def test_opt_params_override_smoke():
    inp = FEASIBLE_CASES["readme"]
    sp = SpiralTorsionSpring.maximize_stiffness(inp, opt_params={'n': 64, 'iters': 1})
    assert sp.res.success is True
    assert sp.stiffness > 0


# --- exhaustive expectation parity (cheap roll-up) ------------------------

@pytest.mark.parametrize("name", list(CASES))
def test_case_matches_expectation(name):
    c = CASES[name]
    if c["expected"] == "feasible":
        sp = SpiralTorsionSpring.maximize_stiffness(c["inputs"])
        assert sp.res.success is True, f"{name}: {sp.res.message}"
    else:
        with pytest.raises(ValueError):
            SpiralTorsionSpring.maximize_stiffness(c["inputs"])
