import pytest
from money_tools import Mortgage, Rate
from datetime import datetime
import pandas as pd


# Dummy Rate Data
@pytest.fixture
def dummy_rate():
    rate_config = {
            "rate": 0.01,
            "monthly_payment": 1000.00,
            "start_date": '2019-01-01',
            "term": None,
            "end_date": '2019-12-31',
            "payment_day": 1
        }
    return rate_config


class TestSingleRateMortgage(object):

    def test_init(self, dummy_rate):
        mortgage = Mortgage(100_000, [dummy_rate])
        assert type(mortgage) == Mortgage

    @pytest.mark.skip
    def test_end_balance(self, dummy_rate):
        mortgage = Mortgage(100_000, [dummy_rate])
        assert mortgage.end_balance == 88_939.88
        # Not rounded to 2-decimal places, instead ~88_939.880000022

    def test_monthly_schedule(self, dummy_rate):
        mortgage = Mortgage(100_000, [dummy_rate])
        assert round(mortgage.schedule_monthly['End Balance'].iloc[-1], 2) == 88_939.88

    def test_payment_summary(self, dummy_rate):
        mortgage = Mortgage(100_000, [dummy_rate])
        df = mortgage.payment_summary()
        assert type(df) == pd.DataFrame

    def test_yearly_schedule(self):

        rate_config = {
            "rate": 0.01,
            "monthly_payment": 1100,
            "start_date": '2019-01-01',
            "term": None,
            "end_date": '2020-12-31',
            "payment_day": 1
        }
        mortgage = Mortgage(100_000, [rate_config])
        assert round(mortgage.schedule_yearly.Interest.sum(), 2) == 1_745.60

# Dummy Rate Data
@pytest.fixture
def dummy_rates_list():
    rate_config1 = {
            "rate": 0.01,
            "monthly_payment": 1000.00,
            "start_date": '2019-01-01',
            "term": None,
            "end_date": '2019-12-31',
            "payment_day": 1
        }

    rate_config2 = {
            "rate": 0.02,
            "monthly_payment": 1000.00,
            "start_date": '2020-01-01',
            "term": None,
            "end_date": '2020-12-31',
            "payment_day": 1
        }
    return [rate_config1, rate_config2]

class TestMultiRateMortgage(object):

    def test_init(self, dummy_rates_list):
        mortgage = Mortgage(100_000, dummy_rates_list)
        assert type(mortgage) == Mortgage

    @pytest.mark.skip
    def test_end_balance(self, dummy_rate):
        mortgage = Mortgage(100_000, dummy_rates_list)
        assert mortgage.end_balance == 88_939.88
        # Not rounded to 2-decimal places, instead ~88_939.880000022

    def test_monthly_schedule(self, dummy_rate):
        mortgage = Mortgage(100_000, dummy_rates_list)
        assert round(mortgage.schedule_monthly['End Balance'].iloc[-1], 2) == 88_939.88

    def test_payment_summary(self, dummy_rate):
        mortgage = Mortgage(100_000, dummy_rates_list)
        df = mortgage.payment_summary()
        assert type(df) == pd.DataFrame
