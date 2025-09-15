from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np
import math 

class Trader:

    def __init__(self):
        self.prices_history = {"STARFRUIT": [], "AMETHYSTS": []}
        self.position_limit = 20
        self.short_term_window = 5
        self.long_term_window = 50

    def moving_average(self, prices: List[float], window: int) -> float:
        if len(prices) < window:
            return sum(prices) / len(prices)
        return sum(prices[-window:]) / window

    def calculate_volatility(self, prices: List[float]) -> float:
        if len(prices) < 2:
            return 0
        price_changes = [j - i for i, j in zip(prices, prices[1:])]
        return np.std(price_changes)

    def run(self, state: TradingState):
        result = {}
        trade_history = state.own_trades
        current_positions = state.position
        for product, order_depth in state.order_depths.items():
            orders = []
            #current_volatility = self.calculate_volatility(self.prices_history[product])
            #is_high_volatility = current_volatility > self.high_volatility_threshold
            if product == "STARFRUIT":
                if current_positions.get(product) is None:
                   current_positions[product] = 0

                if len(order_depth.sell_orders) > 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                if len(order_depth.buy_orders) > 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    current_mid_price = int((best_ask + best_bid) / 2)
                else:
                    continue
                self.prices_history[product].append(current_mid_price)
                if len(self.prices_history[product]) > 100: # this value here should be the same as the long term window 
                    self.prices_history[product].pop(0)

                orders.append(Order(product, best_ask, best_ask_volume))

                traded_buy_prices, traded_sell_prices  = [], []
                for symbol, trades in trade_history.items():
                    if symbol == product: 
                        for trade in trades:
                            if trade.quantity > 0:
                                traded_buy_prices.append(trade.price)
                            else: 
                                traded_sell_prices.append(trade.price)

                if any(traded_buy_prices):
                    max_traded_buy_prices = max(traded_buy_prices)
                else:
                    max_traded_buy_prices = math.inf

                if any(traded_sell_prices):
                    min_traded_sell_prices = min(traded_sell_prices)
                else:
                    min_traded_sell_prices = -math.inf

                if current_positions[product] > 0 and max_traded_buy_prices < best_bid:
                    orders.append(Order(product, best_bid, -current_positions[product]))
                elif current_positions[product] < 0 and min_traded_sell_prices > best_ask:
                    orders.append(Order(product, best_ask, current_positions[product]))
                    

                short_term_ma = self.moving_average(self.prices_history[product], self.short_term_window)
                long_term_ma = self.moving_average(self.prices_history[product], self.long_term_window)

                if short_term_ma > long_term_ma and current_positions[product] < self.position_limit and current_positions[product] >= 0:
                    quantity = min(order_depth.sell_orders[best_ask], self.position_limit - current_positions[product])
                    orders.append(Order(product, best_ask, quantity))
                   
                elif short_term_ma < long_term_ma and current_positions[product] > -self.position_limit and current_positions[product] <= 0:
                    quantity = min(order_depth.buy_orders[best_bid], self.position_limit + current_positions[product])
                    orders.append(Order(product, best_bid, -quantity))
                  
                
            elif product == "AMETHYSTS":
                if current_positions.get(product) is None:
                   current_positions[product] = 0
                # Initialize the list of Orders to be sent as an empty list

                # Define a fair value for the PEARLS.
                # Note that this value of 10000 is just a dummy value, you should likely change it!
                acceptable_price = 9999.9

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:
                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        quantity = max(0,min(-best_ask_volume, 20 - current_positions[product]))
                        orders.append(Order(product, best_ask, quantity))
                        
                if len(order_depth.buy_orders) > 0:
                   best_bid = max(order_depth.buy_orders.keys())
                   best_bid_volume = order_depth.buy_orders[best_bid]
                   if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        quantity = -max(0,min(best_bid_volume, 20 + current_positions[product]))
                        orders.append(Order(product, best_bid, quantity))


            result[product] = orders

        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData