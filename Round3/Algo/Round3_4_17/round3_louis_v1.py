from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import pandas as pd
import numpy as np
import math 

class Trader:
    def run(self, state: TradingState):
        result = {"CHOCOLATE": [], "ROSES": [], "STRAWBERRIES": [], "GIFT_BASKET": []}

        for product in ["CHOCOLATE", "ROSES", "STRAWBERRIES"]:
            ask_price = list(state.order_depths[product].sell_orders.keys())
            bid_price = list(state.order_depths[product].buy_orders.keys())
            mid_price = [(ask + bid)/2 for ask, bid in zip(ask_price, bid_price)]
            mid_series = pd.Series(mid_price)
            exp12 = mid_series.ewm(span = 12, adjust = False).mean()
            exp26 = mid_series.ewm(span = 26, adjust = False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span = 9, adjust = False).mean()

            # Initialize results
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            order_depth_gift = state.order_depths["GIFT_BASKET"]
            best_ask_gift = list(order_depth_gift.sell_orders.keys())[0]
            best_bid_gift = list(order_depth_gift.buy_orders.keys())[0]
            gift_mid_price = (best_ask_gift + best_bid_gift) / 2

            best_bid = list(order_depth.buy_orders.keys())[0] 
            best_ask = list(order_depth.sell_orders.keys())[0] 
            best_mid = (best_bid + best_ask) / 2
            # Trading Strategies
            if (macd <= signal).any(): # Selling logic
                quantity_sell = order_depth.buy_orders[best_bid]
                orders.append(Order(product, best_bid, -quantity_sell))
                if product in ["CHOCOLATE", "STRAWBERRIES"]:
                    quantity = math.ceil(quantity_sell * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_ask_gift, quantity))
                elif product == "ROSES":
                    quantity = math.floor(quantity_sell * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_ask_gift, quantity))

            if (macd > signal).any(): # Buying logic
                quantity_buy = order_depth.sell_orders[best_ask]
                orders.append(Order(product, best_ask, -quantity_buy))
                if product in ["CHOCOLATE", "STRAWBERRIES"]:
                    quantity = math.ceil(quantity_buy * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_bid_gift, quantity))
                elif product == "ROSES":
                    quantity = math.floor(quantity_buy * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_bid_gift, quantity))

            result[product] = orders

            traderData = 'Hello World'
            conversions = 0

        return result, conversions, traderData
