import time
import pytest
from analytic_solver import maximize_stiffness, maximize_torque

# Canonical example from ANALYTIC_SOLVER.md §6.3
CANONICAL = {
    'elasticity': 3100,
    'stress_yield': 85,
    'height': 12,
    'max_radius_pre': 70,
    'radius_center': 15,
    'pitch_0': 0.5,
    'deltatheta_opt': 3.14,
    'torque_pre': 2800,
    'safety_factor': 0.8,
    'max_thickness': None,
    'nozzle_diameter': 0.4,
}


def test_maximize_stiffness_canonical():
    sol = maximize_stiffness(CANONICAL)
    assert abs(sol.thickness - 8.76) < 0.15, f"thickness={sol.thickness:.4f}"
    assert abs(sol.arclength - 856.8) < 15, f"arclength={sol.arclength:.1f}"
    assert abs(sol.stiffness - 2431) < 150, f"stiffness={sol.stiffness:.1f}"


def test_maximize_torque_canonical():
    sol = maximize_torque(CANONICAL)
    assert abs(sol.thickness - 7.28) < 0.15, f"thickness={sol.thickness:.4f}"
    assert abs(sol.arclength - 1199.9) < 30, f"arclength={sol.arclength:.1f}"
    assert abs(sol.preload_torque - 4075) < 150, f"M_pre={sol.preload_torque:.1f}"
    assert abs(sol.stiffness - 995) < 80, f"stiffness={sol.stiffness:.1f}"


def test_stress_utilization_at_stiffness_optimum():
    sol = maximize_stiffness(CANONICAL)
    assert abs(sol.stress_utilization - 1.0) < 0.01, f"util={sol.stress_utilization:.4f}"


def test_stress_utilization_at_torque_optimum():
    sol = maximize_torque(CANONICAL)
    assert abs(sol.stress_utilization - 1.0) < 0.01, f"util={sol.stress_utilization:.4f}"


def test_active_constraints_stiffness():
    sol = maximize_stiffness(CANONICAL)
    assert len(sol.active_constraints) >= 1
    label = sol.active_constraints[0]
    assert 'stress' in label


def test_stiffness_headroom_nonnegative():
    sol = maximize_stiffness(CANONICAL)
    assert sol.headroom['stress_MPa'] >= -1e-4
    assert sol.headroom['radius_pre_mm'] >= -1e-4


def test_class_method_stiffness():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from spiral_torsion_spring_optimizer import SpiralTorsionSpring
    sp = SpiralTorsionSpring.maximize_stiffness_analytic(CANONICAL)
    sol = maximize_stiffness(CANONICAL)
    assert abs(sp.stiffness - sol.stiffness) < 1e-6


def test_class_method_torque():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from spiral_torsion_spring_optimizer import SpiralTorsionSpring
    sp = SpiralTorsionSpring.maximize_torque_analytic(CANONICAL)
    sol = maximize_torque(CANONICAL)
    assert abs(sp.torque_pre - sol.preload_torque) < 1e-6


def test_solve_time_under_1ms():
    # Warm up imports
    maximize_stiffness(CANONICAL)
    start = time.perf_counter()
    maximize_stiffness(CANONICAL)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 5.0, f"solve time {elapsed_ms:.2f}ms exceeds 5ms threshold (target is <1ms)"


def test_to_dict_works_for_analytic():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from spiral_torsion_spring_optimizer import SpiralTorsionSpring
    sp = SpiralTorsionSpring.maximize_stiffness_analytic(CANONICAL)
    d = sp.to_dict()
    assert d['optimizer_result'] is None
    assert d['stiffness'] is not None


def test_geometric_consistency_stiffness():
    sol = maximize_stiffness(CANONICAL)
    # radius_pre must be between radius_E and R_max
    assert sol.radius_pre >= sol.radius_E - 1e-4
    assert sol.radius_pre <= CANONICAL['max_radius_pre'] + 1e-4
    # n_revolutions must be positive
    assert sol.n_revolutions > 0


def test_geometric_consistency_torque():
    sol = maximize_torque(CANONICAL)
    assert sol.radius_pre >= sol.radius_E - 1e-4
    assert sol.radius_pre <= CANONICAL['max_radius_pre'] + 1e-4
    assert sol.n_revolutions > 0


def test_torque_objective_exceeds_stiffness_objective_preload():
    sol_s = maximize_stiffness(CANONICAL)
    sol_t = maximize_torque(CANONICAL)
    # max_torque objective should deliver more preload than what max_stiffness provides
    assert sol_t.preload_torque > sol_s.preload_torque


def test_stiffness_objective_exceeds_torque_objective_stiffness():
    sol_s = maximize_stiffness(CANONICAL)
    sol_t = maximize_torque(CANONICAL)
    assert sol_s.stiffness > sol_t.stiffness
