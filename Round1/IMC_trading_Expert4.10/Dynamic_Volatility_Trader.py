from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
from collections import deque
import numpy as np

class Trader:

    def __init__(self):
        self.prices_history = {"STARFRUIT": deque(maxlen=30), "AMETHYSTS": deque(maxlen=30)}  # Increased to calculate volatility
        self.positions = {"STARFRUIT": 0, "AMETHYSTS": 0}
        self.position_limit = 20
        self.short_term_window = 5
        self.long_term_window = 20
        self.volatility_window = 10  # Window to calculate volatility
        self.high_volatility_threshold = 0.05  # Placeholder threshold for high volatility

    def moving_average(self, prices: deque, window: int) -> float:
        if len(prices) < window:
            return sum(prices) / len(prices)
        else:
            return sum(list(prices)[-window:]) / window

    def calculate_volatility(self, prices: deque) -> float:
        if len(prices) < 2:
            return 0
        price_changes = [j - i for i, j in zip(prices, prices[1:])]
        return np.std(price_changes)

    def run(self, state: TradingState):
        result = {}
        for product, order_depth in state.order_depths.items():
            orders = []
            
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                current_mid_price = (best_ask + best_bid) / 2
            else:
                continue
            
            self.prices_history[product].append(current_mid_price)
            
            # Adjust strategy based on timestamp and calculated volatility
            current_volatility = self.calculate_volatility(self.prices_history[product])
            is_high_volatility = current_volatility > self.high_volatility_threshold
            timestamp = state.timestamp
            
            # STARFRUIT - Adjusting for Volatility and Timestamp
            if product == "STARFRUIT":
                short_term_ma = self.moving_average(self.prices_history[product], self.short_term_window)
                long_term_ma = self.moving_average(self.prices_history[product], self.long_term_window)
                # Adjust sensitivity based on volatility and timestamp
                sensitivity_multiplier = 2 if is_high_volatility and timestamp > 100000 else 1
                ma_difference = abs(short_term_ma - long_term_ma) * sensitivity_multiplier
                
                if short_term_ma > long_term_ma and ma_difference > self.high_volatility_threshold:
                    quantity = min(order_depth.sell_orders[best_ask], self.position_limit - self.positions[product])
                    orders.append(Order(product, best_ask, quantity))
                    self.positions[product] += quantity
                elif short_term_ma < long_term_ma and ma_difference > self.high_volatility_threshold:
                    quantity = min(order_depth.buy_orders[best_bid], self.position_limit + self.positions[product])
                    orders.append(Order(product, best_bid, -quantity))
                    self.positions[product] -= quantity
            
            # AMETHYSTS - Dynamic Mean Reversion Adjusted for Volatility
            elif product == "AMETHYSTS":
                dynamic_mean = self.moving_average(self.prices_history[product], self.long_term_window)
                # Adjust the buying/selling threshold based on volatility
                threshold_adjustment = current_volatility * sensitivity_multiplier
                if abs(current_mid_price - dynamic_mean) > threshold_adjustment:
                    if current_mid_price < dynamic_mean:
                        quantity = min(order_depth.sell_orders[best_ask], self.position_limit - self.positions[product])
                        orders.append(Order(product, best_ask, quantity))
                        self.positions[product] += quantity
                    elif current_mid_price > dynamic_mean:
                        quantity = min(order_depth.buy_orders[best_bid], self.position_limit + self.positions[product])
                        orders.append(Order(product, best_bid, -quantity))
                        self.positions[product] -= quantity
            
            result[product] = orders
        
        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData