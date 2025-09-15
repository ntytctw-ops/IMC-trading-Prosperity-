from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
import statistics

class Trader:
    def __init__(self):
        self.foreign_ask = []
        self.foreign_bid = []
        self.want_to_export_quantity = 0
        self.want_to_export = 0
        self.want_to_import_quantity = 0
        self.want_to_import = 0
        self.arb_quantity = 0
        self.want_to_convert = 0
        self.position_limit = {"ORCHIDS": 100}

    def storage_fee(self, duration, quantity):
        return 0.1 * duration * quantity
    
    def foreign_bid_price(self,conversion_obv, quantity):
        return conversion_obv.bidPrice - conversion_obv.exportTariff - conversion_obv.transportFees - self.storage_fee(1, quantity)

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

        local_ask_list = list(state.order_depths['ORCHIDS'].sell_orders.keys())
        local_bid_list = list(state.order_depths['ORCHIDS'].buy_orders.keys())
        best_local_ask = min(local_ask_list) # min ask price
        best_local_bid = max(local_bid_list) # max bid price 
        best_ask_quantity = state.order_depths['ORCHIDS'].sell_orders[best_local_ask] # <0 
        best_bid_quantity = state.order_depths['ORCHIDS'].buy_orders[best_local_bid] # >0 

        foreign_ask_price = conversion_obv.askPrice + conversion_obv.importTariff + conversion_obv.transportFees

        #arbitrage1: foreign bid > local ask price, we buy from local and then export the next round
        '''quantity = int(best_ask_quantity / 2)
        print("Foreign_bid", self.foreign_bid_price(conversion_obv, quantity))
        buy_price = best_local_bid + 1
        print("buy price is", buy_price)
        if self.foreign_bid_price(conversion_obv, quantity) > buy_price:
            orders.append(Order(product, buy_price, quantity)) # we want to buy here 
            self.want_to_convert = 1'''

        #arbitrage2: foreign ask < local sell price, we can short sell at local first, then import 
        sell_price_1 = best_local_ask - 1
        quantity_1 = 100 #>0
        sell_price_2 = best_local_ask - 2
        quantity_2 = 100 #>0
        sell_price_3 = best_local_ask - 3
        quantity_3 = 100 #>0
        print("foreign ask price is", foreign_ask_price)
        print("sell price is", sell_price_1), 
        if sell_price_2 <= foreign_ask_price < sell_price_1: 
            orders.append(Order(product, sell_price_1, -quantity_1)) # we sell at a lower local ask price
            self.want_to_convert = 1
        if sell_price_3 <= foreign_ask_price < sell_price_2: 
            orders.append(Order(product, sell_price_2, -quantity_2)) # we sell at a lower local ask price
            self.want_to_convert = 1
        if foreign_ask_price < sell_price_3: 
            orders.append(Order(product, sell_price_3, -quantity_3)) # we sell at a lower local ask price
            self.want_to_convert = 1
            
        if self.want_to_convert == 1:
            conversions  = -quantity_position
            self.want_to_convert = 0
        
        
        
        traderData = "SAMPLE"  # Placeholder value

        result[product] = orders
        print("Conversions = ", conversions)
        if product in state.position:
            print("Position is", state.position[product])

        return result, conversions, traderData