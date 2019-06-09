# import pandas as pd
# import numpy as np
# from datetime import datetime, date, timedelta
# import matplotlib.pyplot as plt

import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
import calendar


def amortize(principal: float, interest_rate: float, years: int=25, monthly_pmt: float=None, addl_principal: float=0, 
             start_date: date=date.today(), end_date: date=None, payment_day: int=1
    ):
    """Creates the amortization table entries.
    
    Parameters
    ----------
    principal : float
        Starting loan amount.
    interest_rate : float
        The interest rate expressed as a decimal.
    years : int, optional
        Number of years for the loan, by default 25
    monthly_pmt : float, optional
        The regular monthly payment amount, by default None
    addl_principal : float, optional
        Any additional monthly payment made at the same time as the monthly_pmt, by default 0
    start_date : date, optional
        Starting date to build amortisation table, by default today's date
    end_date : date, optional
        End date to build the amortisation table up to, by default the start date plus the number of years
    payment_day : int, optional
        Day of the month when monthly payments are taken, by default 1 for the first day of the month

    Yields
    ------
    OrderedDict

    """
    ANNUAL_PAYMENTS = 365  # TODO deal with leap years

    # TODO: move to class init
    if not end_date:
        end_date = start_date+relativedelta(years=years)

    if not monthly_pmt:
        monthly_pmt = -round(np.pmt(interest_rate/12, years*12, principal), 2)

    # initialize the variables to keep track of the periods and running balances
    p = 1
    beg_balance = round(principal, 2)
    end_balance = round(beg_balance, 2)
    running_date = start_date

    while end_balance > 0 and running_date < start_date+relativedelta(years=years):

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
    return pd.DataFrame(amortize(*args, **kwargs))


class Mortgage(object):
    """
    Mortgage Class, for calculating mortgage interest, payments, etc...
    """
    
    def __init__(self, principal, term, annual_interest_rate, monthly_payment, start_date=date.today(),
                 end_date=None, payment_day=1):
        self.principal = principal
        self.term = term
        self.annual_interest_rate = annual_interest_rate
        self.interest_calculated = 'daily'
        self.monthly_payment = monthly_payment
        self.start_date = start_date
        self.end_date = end_date
        self.payment_day = payment_day
        
        # make daily schedule
        self.schedule = self.calc_schedule()
        
        # Schedules expressed in other time granularities
        self.schedule_monthly = self.calc_schedule_monthly()
        self.schedule_yearly = self.calc_schedule_yearly()        
        
    def __repr__(self):
        return '<Mortgage(principal={principal}, term={term}, annual_interest_rate={annual_interest_rate})>'\
                    .format(principal=self.principal,
                            term=self.term,
                            annual_interest_rate=self.annual_interest_rate)
    
    def calc_schedule(self):
        """Daily payment schedule, accounting for interest paid daily"""
        schedule = amortize_table(self.principal,
                                  self.annual_interest_rate,
                                  years=self.term,
                                  monthly_pmt=self.monthly_payment,
                                  start_date=self.start_date,
                                  end_date=self.end_date,
                                  payment_day=self.payment_day)
        
        # Ensure dt dtype
        schedule['Date'] = pd.to_datetime(schedule['Date'])
        schedule['Date'] = schedule['Date']
        
        return schedule
    
    def calc_schedule_monthly(self):
        """Aggregate the schedule to Month Level"""
        schedule = self.schedule
        
        schedule['year'] = schedule['Date'].dt.year
        schedule['month'] = schedule['Date'].dt.month
        schedule['day'] = schedule['Date'].dt.day
        schedule['end_day'] = schedule[['year', 'month']].apply(lambda x: calendar.monthrange(x.year, x.month)[1],
                                                                axis=1)


        schedule_mon = schedule\
            .groupby(['year', 'month'])\
            .agg({'Payment': 'sum',
                  'Interest': 'sum',
                  'Additional_Payment': 'sum'
                 }
                )

        schedule_mon.index.names = ['year', 'month']
        schedule_mon.reset_index(inplace=True)
        
        month_end_balances = schedule.loc[schedule['day'] == schedule['end_day'], 
                                          ['year', 'month', 'End Balance']]

        
        schedule_mon = schedule_mon.merge(month_end_balances, how='inner', on=['year', 'month'])
        
        schedule_mon['day'] = 1 # start of month
        schedule_mon['Month Date'] = pd.to_datetime(schedule_mon[['year', 'month', 'day']])

        # Monthly principal amounts    
        schedule_mon['Principal'] = schedule_mon['Payment'] - schedule_mon['Interest']
        
        schedule_mon.drop(['day', 'month', 'year'], axis=1, inplace=True)
        
        return schedule_mon
        
    def calc_schedule_yearly(self):
        """Aggregate the schedule to years"""
        
        schedule = self.schedule

        # Yearly
        start_date = schedule['Date'].min()
        schedule['years_out'] = schedule['Date'].apply(lambda x: relativedelta(x, start_date).years)
        schedule['end_of_year_window'] = schedule['years_out'].diff(-1).fillna(-1).abs()
        
        schedule_yr = schedule\
            .groupby([schedule['years_out']])\
            .agg({'Payment': 'sum',
                  'Interest': 'sum',
                  'Additional_Payment': 'sum',
                  'Date': 'min',
                  'Date': 'max'
                 }
                )

        schedule_yr.reset_index(drop=False, inplace=True)
        schedule_yr['Principal'] = schedule_yr['Payment'] - schedule_yr['Interest']
        
        yearly_end_balances = schedule.loc[schedule['end_of_year_window'] == 1, 
                                           ['years_out', 'End Balance']]

        schedule_yr = schedule_yr.merge(yearly_end_balances, how='inner', on=['years_out'])

        return schedule_yr
        
    def payment_summary(self, start_date=None, end_date=None):
        """Summary of cost of mortgage between two dates"""
        
        if not start_date:
            start_date = self.start_date
        
        if not end_date:
            end_date = self.end_date
        
        df = self.schedule \
                 .loc[(self.schedule['Date'] >= start_date) & (self.schedule['Date'] <= end_date), :]
        
        summary = pd.DataFrame({'Start Balance': [df['Begin Balance'].max()],
                                'Total Payments': [df['Payment'].sum()],
                                'Total Interest': [df['Interest'].sum()],
                                'Total Additional Payments': [df['Additional_Payment'].sum()],
                                'End Balance': df.loc[df['Date'] == end_date, 'End Balance'].values,
                                'Start Date': [df['Date'].min()],
                                'End Date': [df['Date'].max()]},
                               index=None)
        
        return summary
