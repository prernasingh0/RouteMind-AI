from uuid import uuid4
import pytest
from app.services.operations import DistanceCalculator


def test_distance_calculator_is_symmetric() -> None:
    calculator = DistanceCalculator()
    assert calculator.kilometers((40.7128, -74.0060), (51.5074, -0.1278)) == pytest.approx(calculator.kilometers((51.5074, -0.1278), (40.7128, -74.0060)), rel=1e-10)
    assert calculator.kilometers((0, 0), (0, 0)) == 0
