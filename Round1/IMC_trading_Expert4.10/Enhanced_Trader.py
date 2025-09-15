from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np

class Trader:
    
    def __init__(self):
        self.prices = {"STARFRUIT": [], "AMETHYSTS": []}
        self.short_window = 5
        self.long_window = 20
        
    def calculate_moving_averages(self, prices, window):
        return np.convolve(prices, np.ones(window), 'valid') / window
    
    def run(self, state: TradingState):
        result = {}
        for product, order_depth in state.order_depths.items():
            orders = []
            
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                current_mid_price = (best_ask + best_bid) / 2
                self.prices[product].append(current_mid_price)
                
                if product == "STARFRUIT":
                    if len(self.prices[product]) >= self.long_window:
                        short_ma = self.calculate_moving_averages(self.prices[product], self.short_window)[-1]
                        long_ma = self.calculate_moving_averages(self.prices[product], self.long_window)[-1]
                        
                        if short_ma > long_ma and len(order_depth.sell_orders) > 0:  # Buy signal
                            quantity = order_depth.sell_orders[best_ask]
                            orders.append(Order(product, best_ask, quantity))
                        elif short_ma < long_ma and len(order_depth.buy_orders) > 0:  # Sell signal
                            quantity = order_depth.buy_orders[best_bid]
                            orders.append(Order(product, best_bid, -quantity))
                            
                elif product == "AMETHYSTS":
                    if len(self.prices[product]) >= self.long_window:
                        mean_price = np.mean(self.prices[product][-self.long_window:])
                        std_price = np.std(self.prices[product][-self.long_window:])
                        
                        if current_mid_price < mean_price - std_price and len(order_depth.sell_orders) > 0:  # Buy signal
                            quantity = order_depth.sell_orders[best_ask]
                            orders.append(Order(product, best_ask, quantity))
                        elif current_mid_price > mean_price + std_price and len(order_depth.buy_orders) > 0:  # Sell signal
                            quantity = order_depth.buy_orders[best_bid]
                            orders.append(Order(product, best_bid, -quantity))
            
            result[product] = orders
        
        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData