"""
Unit tests for Kinetic Translation Deficit (KTD) processing.
"""
import pytest
import pandas as pd
from src.ktd_metrics import KTDProcessor


def test_ktd_processor_initialization():
    processor = KTDProcessor(epsilon=0.01)
    assert processor.epsilon == 0.01
