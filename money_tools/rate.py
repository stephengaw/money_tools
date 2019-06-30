"""
Rates that make up a Mortgage.
"""
import pandas as pd
from datetime import datetime, date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
import calendar
import matplotlib.pyplot as plt


def _amortize(principal: float, interest_rate: float, monthly_pmt: float, start_date: date, end_date: date,
              addl_principal: float=0, payment_day: int=1
    ):
    """Creates the amortization table entries.
    
    Parameters
    ----------
    principal : float
        Starting loan amount.
    interest_rate : float
        The interest rate expressed as a decimal.
    monthly_pmt : float
        The regular monthly payment amount
    start_date : date
        Starting date to build amortisation table
    end_date : date
        End date to build the amortisation table up to
    addl_principal : float, optional
        Any additional monthly payment made at the same time as the monthly_pmt, by default 0
    payment_day : int, optional
        Day of the month when monthly payments are taken, by default 1 for the first day of the month

    Yields
    ------
    OrderedDict

    """
    ANNUAL_PAYMENTS = 365  # TODO deal with leap years

    # initialize the variables to keep track of the periods and running balances
    p = 1
    beg_balance = round(principal, 2)
    end_balance = round(beg_balance, 2)
    running_date = start_date

    while end_balance > 0 and running_date <= end_date:

        # Recalculate the interest based on the current balance
        daily_interest = round(((interest_rate/ANNUAL_PAYMENTS) * beg_balance), 2)

        # Payments only made 1 day a month
        if running_date.day == payment_day:
            pmt = round(monthly_pmt, 2)
            # Determine payment based on whether or not this period will pay off the loan
            pmt = min(pmt, beg_balance + daily_interest)
            principal = pmt - daily_interest
            # Ensure additional payment gets adjusted if the loan is being paid off
            addl_pmt = min(round(addl_principal, 2), beg_balance - principal)
        else:
            pmt = 0
            addl_pmt = 0

        # Updated balance at end of day
        end_balance = beg_balance + daily_interest - (pmt + addl_pmt)

        yield OrderedDict([('Date',running_date),
                            ('Period', p),
                            ('Begin Balance', beg_balance),
                            ('Payment', pmt),
                            ('Interest', daily_interest),
                            ('Additional_Payment', addl_pmt),
                            ('End Balance', end_balance)])

        # Increment the counter, balance and date
        p += 1
        running_date += relativedelta(days=1)
        beg_balance = end_balance


def amortize_table(*args, **kwargs):
    """create an amortization table as a dataframe"""
    return pd.DataFrame(_amortize(*args, **kwargs))


dt_fmt = '%Y-%m-%d'

def _parse_date(date_input, error_msg=None):
    """Parse either a string or original date object into a date object
    """
    error_msg = 'Value of date input must be a date object or valid date string.'
    if isinstance(date_input, date):
        return date_input
    elif isinstance(date_input, str):
        return datetime.strptime(date_input, dt_fmt).date()
    else:
        raise ValueError(error_msg)

class Rate:
    """Base class for rates that make up a mortgage/loan
    """

    def __init__(self, start_balance, annual_interest_rate, monthly_payment, start_date=date.today(),
                 term=None, end_date=None, payment_day=1):
        self.start_balance = start_balance
        self.annual_interest_rate = annual_interest_rate
        self.interest_calculated = 'daily'
        self.monthly_payment = monthly_payment
        
        # Parse days
        INVALID_DATE_ERROR_MSG = 'Value of {} must be a date object or valid date string.'
        self.start_date = _parse_date(start_date, error_msg=INVALID_DATE_ERROR_MSG.format('start_date'))
 
        if not term and not end_date:
            raise ValueError('No term or end_date provide, provide one or the other.')
        elif term and not end_date:
            self.end_date = self.start_date + relativedelta(years=term)
        elif not term and end_date:
            self.end_date = _parse_date(end_date, error_msg=INVALID_DATE_ERROR_MSG.format('end_date'))
        elif term and end_date:
            self.end_date = _parse_date(end_date, error_msg=INVALID_DATE_ERROR_MSG.format('end_date'))
            raise Warning('Both term and end_date defined. Defaulting to use end_date value.')
        else:
            raise ValueError('Unexpected values of term and end_date provide.')
        
        self.payment_day = payment_day
        
        # make daily schedule
        self.schedule = self.calc_schedule()
        self.end_balance = self.schedule['End Balance'].iloc[-1]

    def __repr__(self):
        return 'Rate(start_balance={}, annual_interest_rate={}, monthly_payment={}, start_date=\'{}\', end_date=\'{}\')'\
            .format(self.start_balance, self.annual_interest_rate, self.monthly_payment,
                    self.start_date.strftime(dt_fmt), self.end_date.strftime(dt_fmt)
            )

    def calc_schedule(self):
        """Daily payment schedule, accounting for interest paid daily"""
        schedule = amortize_table(self.start_balance,
                                  self.annual_interest_rate,
                                  monthly_pmt=self.monthly_payment,
                                  start_date=self.start_date,
                                  end_date=self.end_date,
                                  payment_day=self.payment_day)
        
        # Ensure dt dtype
        schedule['Date'] = pd.to_datetime(schedule['Date'])
        schedule['Date'] = schedule['Date']
        
        return schedule
