

# ## Actual Calcs

# +
# Low Interest, no overpayment
option1 = Mortgage(270_000,
                    3,
                    0.0163,
                    1167.02,
                    start_date=datetime(2019,7,1),
                    end_date=datetime(2022,6,30),
                    payment_day=7
                   )

low_int_no_overpay = option1.payment_summary()

# -

low_int_no_overpay

# +
# Low Interest, with overpayment
option2 = Mortgage(270_000,
                    3,
                    0.0163,
                    1367.02,
                    start_date=datetime(2019,7,1),
                    end_date=datetime(2022,6,30),
                    payment_day=7
                   )

low_int_with_overpay = option2.payment_summary()
low_int_with_overpay


# +
# Med Interest, with overpayment
option3 = Mortgage(270_000,
                    3,
                    0.0179,
                    1188,
                    start_date=datetime(2019,7,1),
                    end_date=datetime(2022,6,30),
                    payment_day=7
                   )

med_int_no_overpay = option3.payment_summary()
med_int_no_overpay

# +
# Med Interest, with overpayment
option4 = Mortgage(270_000,
                    3,
                    0.0179,
                    1388,
                    start_date=datetime(2019,7,1),
                    end_date=datetime(2022,6,30),
                    payment_day=7
                   )

med_int_with_overpay = option4.payment_summary()
med_int_with_overpay
# -

low_int_no_overpay['Total Interest'] + 999

low_int_with_overpay['Total Interest'] + 999

med_int_no_overpay['Total Interest'] + 299

med_int_with_overpay['Total Interest'] + 299


