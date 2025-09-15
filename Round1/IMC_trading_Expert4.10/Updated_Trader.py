from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    
    def __init__(self):
        self.last_price = {"STARFRUIT": None, "AMETHYSTS": None}
        self.mean_price_amethysts = 10000  # Placeholder for the mean price of AMETHYSTS
    
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
            
            # Strategy for STARFRUIT - Momentum
            if product == "STARFRUIT":
                if self.last_price[product] is not None:
                    if current_mid_price > self.last_price[product]:  # Price is going up, buy
                        if len(order_depth.sell_orders) > 0:
                            quantity = order_depth.sell_orders[best_ask]
                            orders.append(Order(product, best_ask, quantity))
                    elif current_mid_price < self.last_price[product]:  # Price is going down, sell
                        if len(order_depth.buy_orders) > 0:
                            quantity = order_depth.buy_orders[best_bid]
                            orders.append(Order(product, best_bid, -quantity))
            
            # Strategy for AMETHYSTS - Mean Reversion
            elif product == "AMETHYSTS":
                if current_mid_price < self.mean_price_amethysts:  # Price below mean, buy
                    if len(order_depth.sell_orders) > 0:
                        quantity = order_depth.sell_orders[best_ask]
                        orders.append(Order(product, best_ask, quantity))
                elif current_mid_price > self.mean_price_amethysts:  # Price above mean, sell
                    if len(order_depth.buy_orders) > 0:
                        quantity = order_depth.buy_orders[best_bid]
                        orders.append(Order(product, best_bid, -quantity))
            
            self.last_price[product] = current_mid_price
            result[product] = orders
        
        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData