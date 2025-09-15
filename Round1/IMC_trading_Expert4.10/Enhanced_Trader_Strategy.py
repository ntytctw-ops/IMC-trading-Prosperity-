from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
from collections import deque

class Trader:

    def __init__(self):
        self.prices_history = {"STARFRUIT": deque(maxlen=20), "AMETHYSTS": deque(maxlen=20)}
        self.short_term_window = 5
        self.long_term_window = 20

    def moving_average(self, prices: deque, window: int) -> float:
        if len(prices) < window:
            return sum(prices) / len(prices)
        else:
            return sum(list(prices)[-window:]) / window

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
            
            # Update price history
            self.prices_history[product].append(current_mid_price)
            
            # STARFRUIT - Moving Averages Strategy
            if product == "STARFRUIT":
                short_term_ma = self.moving_average(self.prices_history[product], self.short_term_window)
                long_term_ma = self.moving_average(self.prices_history[product], self.long_term_window)
                if short_term_ma > long_term_ma:  # Bullish signal
                    if len(order_depth.sell_orders) > 0:
                        quantity = order_depth.sell_orders[best_ask]
                        orders.append(Order(product, best_ask, quantity))
                elif short_term_ma < long_term_ma:  # Bearish signal
                    if len(order_depth.buy_orders) > 0:
                        quantity = order_depth.buy_orders[best_bid]
                        orders.append(Order(product, best_bid, -quantity))
            
            # AMETHYSTS - Dynamic Mean Reversion
            elif product == "AMETHYSTS":
                dynamic_mean = sum(self.prices_history[product]) / len(self.prices_history[product])
                if current_mid_price < dynamic_mean:  # Price below dynamic mean, buy
                    if len(order_depth.sell_orders) > 0:
                        quantity = order_depth.sell_orders[best_ask]
                        orders.append(Order(product, best_ask, quantity))
                elif current_mid_price > dynamic_mean:  # Price above dynamic mean, sell
                    if len(order_depth.buy_orders) > 0:
                        quantity = order_depth.buy_orders[best_bid]
                        orders.append(Order(product, best_bid, -quantity))
            
            result[product] = orders
        
        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData