"""Validation rules for the shop pipeline.

Table-level problems stop the run. Row-level order problems are sent to quarantine.
"""
import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check

clean_orders_rules = pa.DataFrameSchema({
    "order_id": Column(str, unique=True, nullable=False,
                       checks=Check.str_matches(r"^[A-Z]\d{3}$")),
    "order_date": Column(
        pa.DateTime,
        Check(lambda s: s.dropna() <= pd.Timestamp.now().normalize(),
              error="order date must not be in the future"),
        nullable=True,
    ),
    "customer_id": Column(str, nullable=False),
    "category": Column(str, Check.isin(["Accessories", "Electronics"])),
    "quantity": Column(float, nullable=True),
    "unit_price": Column(float, Check.ge(0), nullable=True),
})

clean_customers_rules = pa.DataFrameSchema({
    "customer_id": Column(str, unique=True, nullable=False,
                          checks=Check.str_matches(r"^C\d{3}$")),
    "customer_name": Column(str, Check.str_length(min_value=2), nullable=False),
    "city": Column(str, nullable=False),
    "email": Column(str, Check.str_matches(r"^$|^[^@\s]+@[^@\s]+\.[^@\s]+$"),
                    nullable=False),
    "country": Column(str, Check.isin(["Germany", "Austria", "Switzerland"]),
                      nullable=False),
    "segment": Column(str, Check.isin(["Private", "Business"]), nullable=False),
})
