from money_tools import amortize_table
from money_tools import Rate
from datetime import datetime
import pandas as pd

class TestAmortisation:

    def test_amortize_table_basic(self):
        amortisation_table = amortize_table(principal=100000,
                                            interest_rate=0.01,
                                            monthly_pmt=1000,
                                            start_date=datetime(2019,1,1),
                                            end_date=datetime(2019,12,31),
                                            addl_principal=0,
                                            payment_day=1)
        assert round(amortisation_table.iloc[-1, -1], 2) == 88_939.88
        # - Interest Calculated at day start
        # - Everythin rounded to 2-decimal places

    def test_amortize_table_added_payments(self):
        amortisation_table = amortize_table(principal=100000,
                                            interest_rate=0.01,
                                            monthly_pmt=1000,
                                            start_date=datetime(2019,1,1),
                                            end_date=datetime(2019,12,31),
                                            addl_principal=100,
                                            payment_day=1)
        assert round(amortisation_table.iloc[-1, -1], 2) == 87_733.23
        # * Expected Google Sheets Result = 87,733.23

    def test_amortize_table_payment_day(self):
        amortisation_table = amortize_table(principal=100000,
                                            interest_rate=0.01,
                                            monthly_pmt=1000,
                                            start_date=datetime(2019,1,1),
                                            end_date=datetime(2019,12,31),
                                            addl_principal=100,
                                            payment_day=10)
        assert round(amortisation_table.iloc[-1, -1], 2) == 87_736.49
        # * Google Sheet Test3 = 87,736.49


class TestRate:

    def test_init(self):
        rate = Rate(start_balance=100000,
                    annual_interest_rate=0.01,
                    monthly_payment=1000,
                    start_date=datetime(2019, 1, 1),
                    end_date=datetime(2019, 12, 31)
                    )
        assert type(rate) == Rate

    def test_schedule(self):
        rate = Rate(start_balance=100000,
                    annual_interest_rate=0.01,
                    monthly_payment=1000,
                    start_date=datetime(2019, 1, 1),
                    end_date=datetime(2019, 12, 31)
                    )
        assert round(rate.schedule['End Balance'].iloc[-1], 2) == 88_939.88

    def test_end_balance(self):
        rate = Rate(start_balance=100000,
                    annual_interest_rate=0.01,
                    monthly_payment=1000,
                    start_date=datetime(2019, 1, 1),
                    end_date=datetime(2019, 12, 31)
                    )
        assert round(rate.end_balance, 2) == 88_939.88

    def test_schedule_multi_year(self):
        rate = Rate(start_balance=100_000,
                    annual_interest_rate=0.01,
                    monthly_payment=1100,
                    start_date=datetime(2019, 1, 1),
                    end_date=datetime(2020,12,31)
                    )
        assert round(rate.schedule['End Balance'].iloc[-1], 2) == 75_345.60
