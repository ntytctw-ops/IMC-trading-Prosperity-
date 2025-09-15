from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            positions = state.position.get(product, 0)  # Get current position or default to 0
            
            if len(order_depth.sell_orders) != 0:
                best_ask, _ = list(order_depth.sell_orders.items())[0]  # Only need the price
                
                if state.timestamp == 0:  # At timestamp 0, buy or sell maximum position (20)
                    if positions < 20:  # Buy
                        print("BUY", str(20 - positions) + "x", best_ask)
                        orders.append(Order(product, best_ask, 20 - positions))
                    elif positions > -20:  # Sell
                        print("SELL", str(20 + positions) + "x", best_ask)
                        orders.append(Order(product, best_ask, -20 - positions))
                
                elif state.timestamp == 100:
                    prev_order_depth: OrderDepth = state.order_depths[product]  # Get order depth for the current timestamp
                    prev_mid_price = int((list(prev_order_depth.sell_orders.keys())[0] + list(prev_order_depth.buy_orders.keys())[0]) / 2)
                    
                    '''if state.timestamp == 100 and prev_mid_price != 0:  # At timestamp 1, calculate positions based on mid price change
                        prev_trade = state.own_trades[product][-1]  # Get the previous trade
                        prev_order_depth = prev_trade.order_depth  # Access the order depth from the previous trade
                        prev_mid_price = int((list(prev_order_depth.sell_orders.keys())[0] + list(prev_order_depth.buy_orders.keys())[0]) / 2)'''
                        
                    if state.position.get(product, 0) > 0:  # If currently long, short 40 positions
                        print("SHORT", str(40) + "x", best_ask)
                        orders.append(Order(product, best_ask, -40))
                    elif state.position.get(product, 0) < 0:  # If currently short, buy 40 positions
                        print("BUY", str(40) + "x", best_ask)
                        orders.append(Order(product, best_ask, 40))
                    else:  # If currently flat, take action based on mid price change
                        if best_ask < prev_mid_price:  # If current mid price dropped by 1 point compared to previous
                            print("SHORT", str(40) + "x", best_ask)
                            orders.append(Order(product, best_ask, -40))
                        elif best_ask > prev_mid_price:  # If current mid price rose by 1 point compared to previous
                            print("BUY", str(40) + "x", best_ask)
                            orders.append(Order(product, best_ask, 40))
                        else:  # If mid price remained the same
                            print("HOLD")
                            orders.append(Order(product, best_ask, 0))
                    
                    if state.timestamp > 100:  # For timestamps greater than 1, compare mid price change
                        prev_trade = state.own_trades[product][-2]  # Get the trade before the previous trade
                        prev_order_depth = prev_trade.order_depth  # Access the order depth from the trade before the previous trade
                        prev_mid_price = (list(prev_order_depth.sell_orders.keys())[0] + list(prev_order_depth.buy_orders.keys())[0]) / 2
                        
                        curr_mid_price = int((best_ask + list(order_depth.buy_orders.keys())[0]) / 2)
                        
                        if curr_mid_price < prev_mid_price:  # If current mid price dropped by 1 point compared to previous
                            print("SHORT", str(40) + "x", best_ask)
                            orders.append(Order(product, best_ask, -40))
                        elif curr_mid_price > prev_mid_price:  # If current mid price rose by 1 point compared to previous
                            print("BUY", str(40) + "x", best_ask)
                            orders.append(Order(product, best_ask, 40))
                        else:  # If mid price remained the same
                            print("HOLD")
                            orders.append(Order(product, best_ask, 0))
                
            result[product] = orders
        
        traderData = "SAMPLE"  # Placeholder value
        conversions = 1  # Placeholder value
        return result, conversions, traderData
