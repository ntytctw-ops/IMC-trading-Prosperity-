from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np

class Trader:
    
    def __init__(self):
        self.prices = {"STARFRUIT": [], "AMETHYSTS": []}
        self.short_ma_window = 5
        self.long_ma_window = 10
        self.std_dev_factor = 2
        
    def calculate_moving_average(self, prices, window):
        if len(prices) < window:
            return None
        return np.mean(prices[-window:])
    
    def calculate_std_dev(self, prices, window):
        if len(prices) < window:
            return None
        return np.std(prices[-window:])
    
    def run(self, state: TradingState):
        result = {}
        for product, order_depth in state.order_depths.items():
            orders = []
            
            # Calculate the current mid price
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                current_mid_price = (best_ask + best_bid) / 2
            else:
                continue  # Skip if there are no bids or asks
                
            self.prices[product].append(current_mid_price)  # Update price history
            
            # Strategy for STARFRUIT - Enhanced Momentum
            if product == "STARFRUIT":
                short_ma = self.calculate_moving_average(self.prices[product], self.short_ma_window)
                long_ma = self.calculate_moving_average(self.prices[product], self.long_ma_window)
                
                if short_ma and long_ma:
                    if short_ma > long_ma and current_mid_price > short_ma:  # Bullish crossover
                        if len(order_depth.sell_orders) > 0:
                            quantity = order_depth.sell_orders[best_ask]
                            orders.append(Order(product, best_ask, quantity))
                    elif short_ma < long_ma and current_mid_price < short_ma:  # Bearish crossover
                        if len(order_depth.buy_orders) > 0:
                            quantity = order_depth.buy_orders[best_bid]
                            orders.append(Order(product, best_bid, -quantity))
            
            # Strategy for AMETHYSTS - Adaptive Mean Reversion
            elif product == "AMETHYSTS":
                rolling_avg = self.calculate_moving_average(self.prices[product], self.long_ma_window)
                std_dev = self.calculate_std_dev(self.prices[product], self.long_ma_window)
                
                if rolling_avg and std_dev:
                    lower_bound = rolling_avg - self.std_dev_factor * std_dev
                    upper_bound = rolling_avg + self.std_dev_factor * std_dev
                    
                    if current_mid_price < lower_bound:  # Below lower threshold, buy
                        if len(order_depth.sell_orders) > 0:
                            quantity = order_depth.sell_orders[best_ask]
                            orders.append(Order(product, best_ask, quantity))
                    elif current_mid_price > upper_bound:  # Above upper threshold, sell
                        if len(order_depth.buy_orders) > 0:
                            quantity = order_depth.buy_orders[best_bid]
                            orders.append(Order(product, best_bid, -quantity))
            
            result[product] = orders
        
        traderData = "Adapt strategy as needed"
        conversions = 1
        return result, conversions, traderData