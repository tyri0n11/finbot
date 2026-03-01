"""Tests for the parse_time helper in services.telegram."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from services.telegram import parse_time


@pytest.mark.parametrize("token,expected", [
    # 12-hour without minutes
    ("7am",   "07:00"),
    ("7pm",   "19:00"),
    ("9AM",   "09:00"),
    ("12am",  "00:00"),  # midnight
    ("12pm",  "12:00"),  # noon
    ("11pm",  "23:00"),
    # 12-hour with minutes
    ("7:30am", "07:30"),
    ("8:30am", "08:30"),
    ("7:30pm", "19:30"),
    ("12:30pm","12:30"),
    # 24-hour
    ("07:00",  "07:00"),
    ("14:30",  "14:30"),
    ("00:00",  "00:00"),
    ("23:59",  "23:59"),
    # Single-digit 24h (treated as hour without meridiem)
    ("9",      "09:00"),
])
def test_parse_time_valid(token, expected):
    assert parse_time(token) == expected


@pytest.mark.parametrize("token", [
    "25:00",   # hour out of range
    "7:60am",  # minute out of range
    "abc",     # not a time
    "",        # empty
    "7 am",    # space not allowed
    "13pm",    # 13pm is invalid (13+12=25)
])
def test_parse_time_invalid(token):
    assert parse_time(token) is None
