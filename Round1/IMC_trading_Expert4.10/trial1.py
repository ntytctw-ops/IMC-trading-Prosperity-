from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict
import numpy as np

class Trader:

    def __init__(self):
        self.prices_history = {"STARFRUIT": [], "AMETHYSTS": []}
        self.positions = {"STARFRUIT": 0, "AMETHYSTS": 0}
        self.position_limit = 20
        self.short_term_window = 20
        self.long_term_window = 100
        #self.volatility_window = 5
        #self.high_volatility_threshold = 0.05

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
        for product in state.order_depths.keys():

            try:
                position = state.position[product]
            except:
                position = 0

        for product, order_depth in state.order_depths.items():
            orders = []
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                current_mid_price = int((best_ask + best_bid) / 2)
            else:
                continue
            
            self.prices_history[product].append(current_mid_price)
            if len(self.prices_history[product]) > 30:
                self.prices_history[product].pop(0)
            #current_volatility = self.calculate_volatility(self.prices_history[product])
            #is_high_volatility = current_volatility > self.high_volatility_threshold

            if product == "STARFRUIT":
                short_term_ma = self.moving_average(self.prices_history[product], self.short_term_window)
                long_term_ma = self.moving_average(self.prices_history[product], self.long_term_window)
                if short_term_ma >= long_term_ma-5 and self.positions[product] < self.position_limit:
                    #if is_high_volatility: 
                    #    continue
                    quantity = min(order_depth.sell_orders[best_ask], self.position_limit - self.positions[product])
                    orders.append(Order(product, best_ask, quantity))
                    self.positions[product] += quantity
                elif short_term_ma <= long_term_ma+5 and self.positions[product] > -self.position_limit:
                    #if is_high_volatility: 
                    #    continue
                    quantity = min(order_depth.buy_orders[best_bid], self.position_limit + self.positions[product])
                    orders.append(Order(product, best_bid, -quantity))
                    self.positions[product] -= quantity

            elif product == "AMETHYSTS":
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 10000 is just a dummy value, you should likely change it!
                acceptable_price = 9999.9

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    # print(type(order_depth.sell_orders))
                    # print(type(order_depth.sell_orders[best_ask]))

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, max(0,min(-best_ask_volume, 20 - position))))
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -max(0,min(best_bid_volume, 20 + position))))

            result[product] = orders

        traderData = "Maintain state if necessary"
        conversions = 1
        return result, conversions, traderData