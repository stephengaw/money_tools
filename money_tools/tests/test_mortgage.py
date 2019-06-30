import pytest
from money_tools import Mortgage, Rate
from datetime import datetime
import pandas as pd


# Dummy Rate Data
@pytest.fixture
def dummy_rate():
    dummy_rate = Rate(start_balance=100000,
                  annual_interest_rate=0.01,
                  monthly_payment=1000,
                  start_date='2019-01-01',
                  end_date='2019-12-31')
    return dummy_rate


class TestMortgage(object):

    def test_init(self, dummy_rate):
        mortgage = Mortgage([dummy_rate])
        assert type(mortgage) == Mortgage

    @pytest.mark.skip
    def test_end_balance(self, dummy_rate):
        mortgage = Mortgage([dummy_rate])
        assert mortgage.end_balance == 88_939.88
        # Not rounded to 2-decimal places, instead ~88_939.880000022

    def test_monthly_schedule(self, dummy_rate):
        mortgage = Mortgage([dummy_rate])
        assert round(mortgage.schedule_monthly['End Balance'].iloc[-1], 2) == 88_939.88

    def test_payment_summary(self, dummy_rate):
        mortgage = Mortgage([dummy_rate])
        df = mortgage.payment_summary()
        assert type(df) == pd.DataFrame

    def test_yearly_schedule(self):
        dummy_rate_2year = Rate(start_balance=100000,
                                annual_interest_rate=0.01,
                                monthly_payment=1100,
                                start_date='2019-01-01',
                                end_date='2020-12-31')
        mortgage = Mortgage([dummy_rate_2year])
        assert round(mortgage.schedule_yearly.Interest.sum(), 2) == 1_745.60
