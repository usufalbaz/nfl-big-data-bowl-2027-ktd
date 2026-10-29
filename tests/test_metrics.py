"""
Comprehensive Unit Test Suite for Kinetic Translation Deficit (KTD)
===================================================================
Validates mathematical integrity, zero-division regularization,
and strategic tier classification.

Author: Yousuf Albaz
License: MIT
"""

import pytest
import numpy as np
import pandas as pd
from src.ktd_metrics import KTDProcessor
from src.validation import assign_strategic_draft_tiers


@pytest.fixture
def sample_combine_data() -> pd.DataFrame:
    """Generates synthetic 10 Hz tracking frames for a prospect cut."""
    return pd.DataFrame({
        "nfl_id": [101, 101, 101, 101],
        "drill_name": ["SPEED_OUT_ROUTE_LEFT"] * 4,
        "s": [7.50, 4.20, 1.10, 6.80],  # Peak entry, decel, apex cut, exit burst
        "time": ["2026-03-01T12:00:00.100", "2026-03-01T12:00:00.200", 
                 "2026-03-01T12:00:00.300", "2026-03-01T12:00:00.400"],
    })


@pytest.fixture
def sample_game_data() -> pd.DataFrame:
    """Generates synthetic regular-season play records."""
    return pd.DataFrame({
        "nfl_id": [101, 101],
        "route_ran": ["OUT", "OUT"],
        "separation_at_pass_forward": [5.50, 6.10],
        "expected_points_added": [0.15, 0.22],
        "yards_after_catch": [4.0, 5.0]
    })


def test_ktd_processor_initialization():
    """Verifies default parameters and epsilon bounds."""
    processor = KTDProcessor(epsilon=0.01)
    assert processor.epsilon == 0.01
    assert isinstance(processor.epsilon, float)


def test_combine_kinematic_extraction(sample_combine_data):
    """Verifies inflection extraction: peak speed, cut apex, and speed drop."""
    processor = KTDProcessor()
    features = processor.extract_combine_cut_kinematics(sample_combine_data, drill_filter="SPEED_OUT")

    assert len(features) == 1
    record = features.iloc[0]
    assert record["nfl_id"] == 101
    assert record["combine_peak_speed"] == 7.50
    assert record["combine_apex_min_speed"] == 1.10
    assert record["combine_speed_drop"] == pytest.approx(6.40, rel=1e-3)
    assert record["combine_velocity_retention"] == pytest.approx(1.10 / 7.50, rel=1e-3)


def test_ktd_metric_calculation(sample_combine_data, sample_game_data):
    """Tests the synthesis of Combine drop and in-game separation into KTD score."""
    processor = KTDProcessor(epsilon=0.01)
    combine_feats = processor.extract_combine_cut_kinematics(sample_combine_data)
    game_feats = processor.extract_game_separation_metrics(sample_game_data, route_target="OUT")

    master = processor.compute_ktd_metric(combine_feats, game_feats)
    
    # Expected separation = mean(5.50, 6.10) = 5.80 yds
    # Expected KTD = 6.40 / (5.80 + 0.01) = 1.101
    assert len(master) == 1
    assert master.iloc[0]["KTD_Score"] == pytest.approx(1.101, abs=0.02)


def test_zero_division_regularization():
    """Ensures KTD handles zero separation without crash (numerical stability)."""
    processor = KTDProcessor(epsilon=0.01)
    combine_feats = pd.DataFrame([{
        "nfl_id": 999,
        "combine_peak_speed": 7.0,
        "combine_apex_min_speed": 2.0,
        "combine_speed_drop": 5.0,
        "combine_velocity_retention": 0.28,
        "combine_mean_speed": 4.5
    }])
    game_feats = pd.DataFrame([{
        "nfl_id": 999,
        "routes_run_count": 1,
        "avg_game_separation": 0.0,  # Zero separation edge-case
        "avg_expected_points_added": -0.1,
        "avg_yards_after_catch": 0.0
    }])

    master = processor.compute_ktd_metric(combine_feats, game_feats)
    # 5.0 / (0.0 + 0.01) = 500.0 (bounded finite value, no ZeroDivisionError)
    assert np.isfinite(master.iloc[0]["KTD_Score"])
    assert master.iloc[0]["KTD_Score"] == 500.0


def test_draft_tier_classification():
    """Verifies prospect categorization thresholds."""
    row_steal = pd.Series({"KTD_Score": 0.99})
    row_starter = pd.Series({"KTD_Score": 1.75})
    row_trap = pd.Series({"KTD_Score": 25.40})

    assert "Tier 1" in assign_strategic_draft_tiers(row_steal)
    assert "Tier 2" in assign_strategic_draft_tiers(row_starter)
    assert "Tier 3" in assign_strategic_draft_tiers(row_trap)
