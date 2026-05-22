from typing import Dict, Any

# Cases for the SHGO optimizer in spiral_torsion_spring_optimizer.py.
# Each "inputs" dict can be passed directly to
# SpiralTorsionSpring.maximize_stiffness(inputs).

# Baseline taken from the README example (a polymer-like spring).
_BASE: Dict[str, Any] = {
    'elasticity': 3100,
    'stress_yield': 85,
    'safety_factor': 0.8,
    'height': 12,
    'max_radius_pre': 70,
    'radius_center': 15,
    'pitch_0': 0.5,
    'deltatheta_opt': 3.14,
    'torque_pre': 2800,
    'min_thickness': None,
    'max_thickness': None,
}

FEASIBLE_CASES: Dict[str, Dict[str, Any]] = {
    "readme":           {**_BASE},
    "large_box":        {**_BASE, 'max_radius_pre': 120, 'torque_pre': 1500},
    "low_torque":       {**_BASE, 'torque_pre': 500},
    "metal_like": {
        'elasticity': 200000, 'stress_yield': 600, 'safety_factor': 1.0,
        'height': 10, 'max_radius_pre': 60, 'radius_center': 10,
        'pitch_0': 1.0, 'deltatheta_opt': 2.0, 'torque_pre': 3000,
        'min_thickness': None, 'max_thickness': None,
    },
    # max_thickness=4.0 binds the upper bound of t; reduced torque_pre keeps
    # the lower bound (driven by torque_pre) below 4.0.
    "max_thickness_binds": {**_BASE, 'torque_pre': 800, 'max_thickness': 4.0},
    # max_radius_pre=50 forces the c3 (max-radius) constraint to be active.
    "max_radius_binds":    {**_BASE, 'max_radius_pre': 50, 'torque_pre': 1500},
    # min_thickness raises the lower thickness bound above the natural floor;
    # 7.0 is below the baseline optimum (~8.76) so the case stays feasible
    # but thickness_bounds[0] should equal 7.0.
    "min_thickness_raised": {**_BASE, 'min_thickness': 7.0},
}

INFEASIBLE_CASES: Dict[str, Dict[str, Any]] = {
    # torque_pre too high: any thickness that survives stress is also
    # geometrically infeasible.
    "infeasible_overload": {**_BASE, 'torque_pre': 500000},
    # max_radius_pre barely above radius_center: c3 unsatisfiable.
    "infeasible_radius":   {**_BASE, 'max_radius_pre': 16},
    # Combination that drives min_arclength_E above max_arclength_E
    # (bounds infeasible, optimizer returns early).
    "degenerate_bounds":   {**_BASE, 'torque_pre': 50000},
}

CASES: Dict[str, Dict[str, Any]] = {
    **{name: {"inputs": inp, "expected": "feasible"}
       for name, inp in FEASIBLE_CASES.items()},
    **{name: {"inputs": inp, "expected": "infeasible"}
       for name, inp in INFEASIBLE_CASES.items()},
}
