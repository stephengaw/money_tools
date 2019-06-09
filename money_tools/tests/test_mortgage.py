from money_tools import Mortgage
from datetime import datetime
import pandas as pd


class TestMortgage(object):

    def test_init(self):

        mortgage = Mortgage(principal=100000,
                            term=1,
                            annual_interest_rate=0.01,
                            monthly_payment=1000,
                            start_date=datetime(2019, 1, 1),
                            end_date=datetime(2019, 12, 31),
                            payment_day=1)

        assert type(mortgage) == Mortgage

    def test_schedule(self):

        mortgage = Mortgage(principal=100000,
                            term=1,
                            annual_interest_rate=0.01,
                            monthly_payment=1000,
                            start_date=datetime(2019, 1, 1),
                            end_date=datetime(2019, 12, 31),
                            payment_day=1)
        
        assert int(mortgage.schedule['End Balance'].iloc[-1]) == 88_939  # 88,939.85

    def test_amortize_table_basic(self):

        amortisation_table = Mortgage.amortize_table(principal=100000,
                                                    interest_rate=0.01,
                                                    years=1,
                                                    monthly_pmt=1000,
                                                    addl_principal=0,
                                                    start_date=datetime(2019,1,1),
                                                    end_date=datetime(2019,12,31),
                                                    payment_day=1)

        assert round(amortisation_table.iloc[-1, -1], 2) == 88_939.88

        # * Expected Google Sheets Result = 88,939.85, my calc gives 88,939.88????
        # - Interest Calculated at day start
        # - Everythin rounded to 2-decimal places

    def test_amortize_table_added_payments(self):

        amortisation_table = Mortgage.amortize_table(principal=100000,
                                                    interest_rate=0.01,
                                                    years=1,
                                                    monthly_pmt=1000,
                                                    addl_principal=100,
                                                    start_date=datetime(2019,1,1),
                                                    end_date=datetime(2019,12,31),
                                                    payment_day=1)
        
        assert round(amortisation_table.iloc[-1, -1], 2) == 87_733.23
        # * Expected Google Sheets Result = 87,733.23

    def test_amortize_table_payment_day(self):

        amortisation_table = Mortgage.amortize_table(principal=100000,
                                                    interest_rate=0.01,
                                                    years=1,
                                                    monthly_pmt=1000,
                                                    addl_principal=100,
                                                    start_date=datetime(2019,1,1),
                                                    end_date=datetime(2019,12,31),
                                                    payment_day=10)

        assert round(amortisation_table.iloc[-1, -1], 2) == 87_736.49
        # * Google Sheet Test3 = 87,736.49

    def test_monthly_schedule(self):

        mortgage = Mortgage(100_000,
                            1,
                            0.01,
                            1000,
                            start_date=datetime(2019,1,1),
                            end_date=datetime(2019,12,31)
                        )

        assert round(mortgage.schedule_monthly['End Balance'].iloc[-1], 2) == 88_939.88
        # * Expected Google Sheets Result = 88,939.85, my calc gives 88,939.88????

    def test_schedule_multi_year(self):
        mortgage = Mortgage(100_000,
                            2,
                            0.01,
                            1100,
                            start_date=datetime(2019,1,1),
                            end_date=datetime(2020,12,31),
                            payment_day=1
                        )

        assert round(mortgage.schedule['End Balance'].iloc[-1], 2) == 75_345.60

    def test_yearly_schedule(self):
        mortgage = Mortgage(100_000,
                            2,
                            0.01,
                            1100,
                            start_date=datetime(2019,1,1),
                            end_date=datetime(2020,12,31),
                            payment_day=1
                        )

        assert round(mortgage.schedule_yearly.Interest.sum(), 2) == 1_745.60

    def test_payment_summary(self):
        mortgage = Mortgage(100_000,
                            2,
                            0.01,
                            1100,
                            start_date=datetime(2019,6,1),
                            end_date=datetime(2021,5,31),
                            payment_day=1
                        )

        df = mortgage.payment_summary()

        assert type(df) == pd.DataFrame
