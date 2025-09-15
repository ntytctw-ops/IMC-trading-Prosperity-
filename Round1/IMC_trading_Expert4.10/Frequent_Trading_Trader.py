from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict

class Trader:

    def __init__(self):
        self.position_limit = 20
        self.max_position_per_trade = 5  # Limit the size per trade to manage risk

    def run(self, state: TradingState):
        result = {}
        for product, order_depth in state.order_depths.items():
            orders = []
            
            # Market Making Strategy: Place buy and sell orders around the current best bid and ask to capture the spread
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                
                # Calculate a mid-price to determine buy and sell levels
                mid_price = (best_ask + best_bid) / 2
                buy_price = mid_price - (mid_price * 0.005)  # 0.5% below mid-price
                sell_price = mid_price + (mid_price * 0.005)  # 0.5% above mid-price
                
                # Ensure the buy and sell prices do not cross existing market prices
                if buy_price < best_bid:
                    orders.append(Order(product, buy_price, self.max_position_per_trade))
                if sell_price > best_ask:
                    orders.append(Order(product, sell_price, -self.max_position_per_trade))
            
            # Order Book Imbalance Strategy: Adjust positions based on the imbalance in the order book
            buy_order_volume = sum(order_depth.buy_orders.values())
            sell_order_volume = sum(order_depth.sell_orders.values())
            total_volume = buy_order_volume + sell_order_volume
            if total_volume == 0:
                continue  # Avoid division by zero
            
            imbalance = (buy_order_volume - sell_order_volume) / total_volume
            # If significant imbalance detected, trade accordingly
            if imbalance > 0.2:  # More buy orders, price might go up
                orders.append(Order(product, best_ask, self.max_position_per_trade))
            elif imbalance < -0.2:  # More sell orders, price might go down
                orders.append(Order(product, best_bid, -self.max_position_per_trade))
            
            result[product] = orders
        
        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData