from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        
        lower_band = 5056.2
        mid_band = 5058.6
        upper_band = 5061.1
        
        for product in state.order_depths:
            if product == 'STARFRUIT':
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    if best_ask < lower_band:  # Buying at the lower Bollinger Band
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))
                    elif best_ask > mid_band:  # Selling half of long positions at mid Bollinger Band
                        print("SELL", str(int(best_ask_amount / 2)) + "x", best_ask)
                        orders.append(Order(product, best_ask, int(best_ask_amount / 2)))
                
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    if best_bid > upper_band:  # Selling at the upper Bollinger Band
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))
                    elif best_bid < mid_band:  # Buying half of short positions at mid Bollinger Band
                        print("BUY", str(-int(best_bid_amount / 2)) + "x", best_bid)
                        orders.append(Order(product, best_bid, -int(best_bid_amount / 2)))
                
                result[product] = orders
    
        traderData = "SAMPLE"  # Placeholder value
        conversions = 1  # Placeholder value
        return result, conversions, traderData
