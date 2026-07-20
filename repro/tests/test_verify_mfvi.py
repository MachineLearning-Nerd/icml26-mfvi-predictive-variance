from pathlib import Path
import importlib.util


MODULE = Path(__file__).parents[1] / "src" / "verify_mfvi.py"
SPEC = importlib.util.spec_from_file_location("verify_mfvi", MODULE)
assert SPEC and SPEC.loader
verify_mfvi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_mfvi)


def test_axis_aligned_design_is_an_equality_case() -> None:
    import numpy as np

    x = np.vstack((np.eye(4), -np.eye(4)))
    row = verify_mfvi.audit_system(x, run_optimizer=True)
    assert abs(float(row["empirical_mfvi_minus_exact_predictive_variance"])) < 1e-12
    assert abs(float(row["first_pc_mfvi_minus_exact_predictive_variance"])) < 1e-12


def test_reverse_kl_gradient_vanishes_at_diagonal_precision_inverse() -> None:
    import numpy as np

    x = np.array([[1.0, 2.0], [-1.0, 0.0], [0.5, -3.0], [-0.5, 1.0]])
    exact, diagonal, precision = verify_mfvi.posterior_and_mfvi(x)
    _, gradient = verify_mfvi.reverse_kl_from_log_diagonal(np.log(diagonal), precision)
    assert np.max(np.abs(gradient)) < 1e-12
    assert np.all(np.linalg.eigvalsh(exact) > 0.0)
