"""
Mortgage class with associated summary and plotting functionality
"""

import pandas as pd
from datetime import date
import numpy as np
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
import calendar
import matplotlib.pyplot as plt
from money_tools import Rate


_general_plot_properties = dict(linewidth=1.0, marker='', linestyle='-')

class Mortgage(object):
    """
    Mortgage Class, for calculating mortgage interest, payments, etc...
    """
    
    def __init__(self, rates: list):
        
        # Check rates not empty
        n_rates = len(rates)
        if n_rates == 0:
            raise ValueError('The list of rates cannot be empty')
        elif n_rates > 1:
            raise NotImplementedError('Only single rate mortgages are currently implemented')
            # TODO: implement multiple rates per mortgage

        # Check all list entries are valid rates
        for rate in rates:
            if type(rate) != Rate:
                raise ValueError(f'All rates must be valid Rate object. Recieved a rate of type {type(rate)}')
        
        rate = rates[0]
        self.start_balance = rate.start_balance
        self.annual_interest_rate = rate.annual_interest_rate
        self.monthly_payment = rate.monthly_payment
        self.start_date = rate.start_date
        self.end_date = rate.end_date
        self.payment_day = rate.payment_day
        self.schedule = rate.schedule
        self.end_balance = rate.end_balance

        # Schedules expressed in other time granularities
        self.schedule_monthly = self.calc_schedule_monthly()
        self.schedule_yearly = self.calc_schedule_yearly()        
        
    def __repr__(self):
        return 'Mortgage()'
        
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

    # Plotting Methods

    def plot_monthly_schedule(self):
        """
        Visual the monthly schedule
        """
        monthly_schedule = self.schedule_monthly

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 10))
        
        # remaining Balance plots
        ax1.plot(monthly_schedule["Month Date"], monthly_schedule["End Balance"], color='r', label='End Balance', **_general_plot_properties)

        # Breakdown of monthly payment plots
        ax2.plot(monthly_schedule["Month Date"], monthly_schedule["Payment"], color='k', label='Payment', **_general_plot_properties)
        ax2.plot(monthly_schedule["Month Date"], monthly_schedule["Interest"], color='b', label='Interest Paid', **_general_plot_properties)
        ax2.plot(monthly_schedule["Month Date"], monthly_schedule["Principal"], color='g', label='Pricipal Paid', **_general_plot_properties)
        
        ax1.set_ylabel('Amount')
        ax2.set_ylabel('Amount')
        ax2.set_xlabel('Payment Month')
        
        # rotate x-labels 45deg
        for tick in ax2.get_xticklabels():
            tick.set_rotation(45)

        ax1.legend()
        ax2.legend()

        ax1.title.set_text('Monthly Payment Schedule')
        
    def plot_cumulative_monthly_schedule(self):
        """
        Visualise the cumulative monthly schedule 
        """

        monthly_schedule = self.schedule_monthly
        
        monthly_schedule['Cumulative Payment'] = monthly_schedule['Payment'].cumsum()
        monthly_schedule['Cumulative Principal'] = monthly_schedule['Principal'].cumsum()
        monthly_schedule['Cumulative Interest'] = monthly_schedule['Interest'].cumsum()
        
        plt.figure()
        plt.plot(monthly_schedule["Month Date"], monthly_schedule["End Balance"], color='r', label='Remaining Balance', **_general_plot_properties)
        plt.plot(monthly_schedule["Month Date"], monthly_schedule["Cumulative Payment"], color='k', label='Cumulative Payments', **_general_plot_properties)
        plt.plot(monthly_schedule["Month Date"], monthly_schedule["Cumulative Principal"], color='b', label='Cumulative Principal Paid', **_general_plot_properties)
        plt.plot(monthly_schedule["Month Date"], monthly_schedule["Cumulative Interest"], color='g', label='Cumulative Interest Paid', **_general_plot_properties)
        
        plt.legend()
        plt.xlabel('Payment Month')
        plt.xticks(rotation=45)
        plt.ylabel('Amount')

        plt.title('Cumulative Monthly Payment Schedule')
