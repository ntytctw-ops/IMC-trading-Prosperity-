from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
import statistics

class Trader:
    def __init__(self):
        self.foreign_ask = []
        self.foreign_bid = []
        self.arb_quantity = 0
        self.position_limit = {"ORCHIDS": 100}
        self.sold_price = 0
        self.sold_time = 0
        self.count = 0

    def run(self, state: TradingState):
        result = {}
        product = "ORCHIDS"
        orders: List[Order] = []
        conversions = 0
        if product in state.position:
            quantity_position = state.position[product]
        else: 
            quantity_position = 0

        conversion_obv = state.observations.conversionObservations[product]

        if product in state.own_trades:
            own_trades = state.own_trades[product]
        else:
            own_trades = []

        local_ask_list = list(state.order_depths['ORCHIDS'].sell_orders.keys())
        local_bid_list = list(state.order_depths['ORCHIDS'].buy_orders.keys())
        best_local_ask = min(local_ask_list) # min ask price
        best_local_bid = max(local_bid_list) # max bid price 
        spread = (best_local_ask - best_local_bid) / 2
        best_ask_quantity = state.order_depths['ORCHIDS'].sell_orders[best_local_ask] # <0 
        best_bid_quantity = state.order_depths['ORCHIDS'].buy_orders[best_local_bid] # >0 

        foreign_ask_price = conversion_obv.askPrice + conversion_obv.importTariff + conversion_obv.transportFees
        self.foreign_ask.append(foreign_ask_price)

        #arbitrage2: foreign ask < local sell price, we can short sell at local first, then import 
        sell_price = int(best_local_ask - spread)
        print("foreign ask price is", foreign_ask_price)
        print("sell price is", sell_price)
        if quantity_position == 0: 
            orders.append(Order(product, sell_price, -77)) # we sell at a lower local ask price
            self.sold_time = state.timestamp
            self.sold_price = 0
        else:
            print("sold time is", self.sold_time)
            for trades in own_trades:
                if trades.timestamp == self.sold_time:
                    self.sold_price = trades.price
            print("sold.price is", self.sold_price)
                
        if state.timestamp <= self.sold_time + 200:
            profit_margin = self.sold_price - foreign_ask_price
            print("profit margin is ", profit_margin)
            if profit_margin >= 0.5:
                conversions = -quantity_position
        else: 
            conversions = -quantity_position
                

        traderData = "SAMPLE"  # Placeholder value

        result[product] = orders
        print("Conversions = ", conversions)
        if product in state.position:
            print("Position is", state.position[product])

        return result, conversions, traderData