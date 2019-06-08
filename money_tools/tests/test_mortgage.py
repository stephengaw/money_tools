from money_tools import Mortgage
from datetime import datetime


def test_mortgage():

    mortgage = Mortgage(principal=100000,
                        term=1,
                        annual_interest_rate=0.01,
                        monthly_payment=1000,
                        start_date=datetime(2019, 1, 1),
                        end_date=datetime(2019, 12, 31),
                        payment_day=1)
    
    assert int(mortgage.schedule['End Balance'].iloc[-1]) == 88_939  # 88,939.85



