from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd
import numpy as np

class Trader:
    def run(self, state: TradingState):
        result = {}

        for product in ["CHOCOLATE", "ROSES", "STRAWBERRIES"]:
            c_ask = list(state.order_depths[product].sell_orders.keys())
            c_bid = list(state.order_depths[product].buy_orders.keys())
            c_mid = [(ask + bid)/2 for ask, bid in zip(c_ask, c_bid)]
            c_mid_series = pd.Series(c_mid)
            exp12 = c_mid_series.ewm(span = 12, adjust = False).mean()
            exp26 = c_mid_series.ewm(span = 26, adjust = False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span = 9, adjust = False).mean()

            # Initialize results
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]

            # Trading Strategies
            if (macd <= signal).any(): # Selling logic
                bid = list(order_depth.buy_orders.keys())[0]
                orders.append(Order(product, bid, -order_depth.buy_orders[bid]))
            if (macd > signal).any(): # Buying logic
                ask = list(order_depth.sell_orders.keys())[0]
                orders.append(Order(product, ask, -order_depth.sell_orders[ask]))

            result[product] = orders

            traderData = 'Hello World'
            conversions = 0

        return result, conversions, traderData
