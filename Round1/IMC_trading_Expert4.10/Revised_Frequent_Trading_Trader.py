from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import math 

class Trader:

    def run(self, state: TradingState):
        result = {}
        for product, order_depth in state.order_depths.items():
            orders = []
            
            if len(order_depth.sell_orders) > 0 or len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                
                # Adjust buy and sell prices to attempt capturing the spread
                buy_price = math.floor(best_bid - (mid_price * 0.01))  
                sell_price = math.ceil(best_ask + (mid_price * 0.01)) 
                
                orders.append(Order(product, buy_price, 10))
                
                orders.append(Order(product, sell_price, -5))
            
            result[product] = orders
        
        traderData = "Updated strategy"
        conversions = 1
        return result, conversions, traderData