# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Daily Mortgage Calculator
#
# Run as:
#
# ```
# Mortgage(270060.03, 23, 0.0179, 1188.00).payment_summary(datetime(2019,7,1), datetime(2020,6,30))
# ```
#

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import matplotlib.pyplot as plt

import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import *


class Mortgage(object):
    """
    Mortgage Class, for calculating mortgage interest, payments, etc...
    """
    
    @staticmethod
    def amortize(principal, interest_rate, years=25, monthly_pmt=None, addl_principal=0, 
                 start_date=date.today(), end_date=None, payment_date=1):
        """
        Create amortization entries for the interest and payment of the loan
        """
        ANNUAL_PAYMENTS = 365  # TODO deal with leap years

        if not end_date:
            end_date = start_date+relativedelta(years=years)

        if not monthly_pmt:
            monthly_pmt = -round(np.pmt(interest_rate/12, years*12, principal), 2)

        # initialize the variables to keep track of the periods and running balances
        p = 1
        beg_balance = principal
        running_date = start_date

        while end_balance > 0 and running_date < start_date+relativedelta(years=years):

            # Recalculate the interest based on the current balance
            daily_interest = round(((interest_rate/ANNUAL_PAYMENTS) * beg_balance), 2)

            # Payments only made 1 day a month
            if running_date.day == payment_date:
                pmt = monthly_pmt
                # Determine payment based on whether or not this period will pay off the loan
                pmt = min(pmt, beg_balance + daily_interest)
                principal = pmt - daily_interest
                # Ensure additional payment gets adjusted if the loan is being paid off
                addl_principal = min(addl_principal, beg_balance - principal)
            else:
                pmt = 0
                addl_principal = 0

            # Updated balance at end of day
            end_balance = beg_balance + daily_interest - (pmt + addl_principal)

            yield OrderedDict([('Date',running_date),
                               ('Period', p),
                               ('Begin Balance', beg_balance),
                               ('Payment', pmt),
                               ('Interest', daily_interest),
                               ('Additional_Payment', addl_principal),
                               ('End Balance', end_balance)])

            # Increment the counter, balance and date
            p += 1
            running_date += relativedelta(days=1)
            beg_balance = end_balance
        
    @staticmethod
    def amortize_table(*args, **kwargs):
        """create an amortization table as a dataframe"""
        return pd.DataFrame(amortize(*args, **kwargs))
    
    def __init__(self, principal, term, annual_interest_rate, monthly_payment):
        self.principal = principal
        self.term = term
        self.annual_interest_rate = annual_interest_rate
        self.interest_calculated = interest_calculated
        self.monthly_payment = monthly_payment
        
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
        schedule = self.amortize_table(self.principal,
                                       self.annual_interest_rate,
                                       years=self.term,
                                       monthly_pmt=self.monthly_payment)
        
        # Ensure dt dtype
        schedule['Date'] = pd.to_datetime(schedule['Date'])
        schedule['Date'] = schedule['Date']
        
        return schedule
    
    def calc_schedule_monthly(self):
        """Aggregate the schedule to Month Level"""
        schedule = self.schedule
        
        schedule_mon = schedule\
            .groupby([schedule['Date'].dt.year, schedule['Date'].dt.month])\
            .agg({'Payment': 'sum',
                  'Interest': 'sum',
                  'Additional_Payment': 'sum',
                  'End Balance': 'min'
                 }
                )

        schedule_mon.index.names = ['year', 'month']
        schedule_mon.reset_index(inplace=True)

        schedule_mon['day'] = 1 # start of month
        schedule_mon['Date'] = pd.to_datetime(schedule_mon[['year', 'month', 'day']])

        # Monthly principal amounts    
        schedule_mon['Principal'] = schedule_mon['Payment'] - schedule_mon['Interest']
        
        return schedule_mon
        
    def calc_schedule_yearly(self):
        """Aggregate the schedule to years"""
        
        schedule = self.schedule

        # Yearly
        start_date = schedule['Date'].min()
        schedule['years_out'] = schedule['Date'].apply(lambda x: relativedelta(x, start_date).years)

        schedule_yr = schedule\
            .groupby([schedule['years_out']])\
            .agg({'Payment': 'sum',
                  'Interest': 'sum',
                  'Additional_Payment': 'sum',
                  'End Balance': 'min',
                  'Date': 'min',
                  'Date': 'max'
                 }
                )

        schedule_yr.reset_index(inplace=True)

        # Monthly principal amounts    
        schedule_yr['Principal'] = schedule_yr['Payment'] - schedule_yr['Interest']

        return schedule_yr
        
    def payment_summary(self, start_date, end_date):
        """Summary of cost of mortgage between two dates"""
        
        df = self.schedule\
                   .loc[(self.schedule['Date'] >= start_date) & (self.schedule['Date'] <= end_date), :]
        
        summary = pd.DataFrame({'Start Balance': [df['Begin Balance'].max()],
                                'Total Payments': [df['Payment'].sum()],
                                'Total Interest': [df['Interest'].sum()],
                                'Total Additional Payments': [df['Additional_Payment'].sum()],
                                'End Balance': [df['End Balance'].min()],
                                'Start Date': [df['Date'].min()],
                                'End Date': [df['Date'].max()]},
                               index=None)
        
        return summary



# +
mortgage = Mortgage(270060.03,
                    23,
                    0.0163,
                    1167.02)

mortgage
# -

mortgage.payment_summary(datetime(2019,7,1), datetime(2020,6,30))

mortgage.schedule_monthly.head()







Mortgage(270060.03, 23, 0.0163, 1167.02).payment_summary(datetime(2019,7,1), datetime(2020,6,30))

Mortgage(270060.03, 23, 0.0179, 1188.00).payment_summary(datetime(2019,7,1), datetime(2020,6,30))





# +
# mortgage.calc_schedule()

mortgage.schedule.head()

# +
a = mortgage.amortize(200000, .02, 25, start_date=date(2019,6,1))

a

# +
schedule = mortgage.amortize_table(200000, .02, 25, start_date=date(2019,6,1))
# schedule = pd.DataFrame(amortize(270060.03, .0163, 5, 1167.02))

schedule.head()
# -

schedule_tots

import seaborn as sns
sns.set()
import matplotlib.pyplot as plt


def plot_results(monthly_schedule):
    """
    Visual the monthly schedule
    """
    
    plt.figure()
    ax = sns.lineplot(x="Date", y="End Balance",
                 markers=True, dashes=False,
                 data=monthly_schedule)
    
    plt.figure()
    ax2 = sns.lineplot(x="Date", y="Payment", markers=True, dashes=False, data=monthly_schedule)
    ax2 = sns.lineplot(x="Date", y="Interest", markers=True, dashes=False, data=monthly_schedule)
    ax2 = sns.lineplot(x="Date", y="Principal", markers=True, dashes=False, data=monthly_schedule)



plot_results(schedule_mon)





schedule_mon.plot('Date', 'End Balance', marker='o')

schedule_mon.plot('Date', 'Interest', marker='o', color='r')
schedule_mon.plot('Date', 'Principal', marker='o', color='g')




