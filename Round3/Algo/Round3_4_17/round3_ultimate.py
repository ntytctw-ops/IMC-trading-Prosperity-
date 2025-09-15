from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import math 
import pandas as pd
import numpy as np 

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT' : 0, 'AMETHYSTS' : 0}
        self.position_limit = {"STARFRUIT": 20, "AMETHYSTS": 20, "ORCHIDS": 100}
        self.foreign_ask = []
        self.foreign_bid = []
        self.arb_quantity = 0
        self.sold_price = 0
        self.sold_time = 0
        self.count = 0

    def total_volume_best_price_calc(self, order_list, buy): # buy = 0 is sell order, buy = 1 is buy order 
        total_volume = 0
        price_list = []
        if buy == 0:
            for price, quantity in order_list:
                total_volume -= quantity
                price_list.append(price)
            return total_volume, min(price_list)
        else:
            for price, quantity in order_list:
                total_volume += quantity
                price_list.append(price)
            return total_volume, max(price_list)

    def compute_orders_amethysts(self, product, order_depth, acc_bid, acc_ask):
        orders: list[Order] = []

        sell_order_list = list(order_depth.sell_orders.items())
        buy_order_list = list(order_depth.buy_orders.items())

        total_ask_volume, best_ask_price = self.total_volume_best_price_calc(sell_order_list, 0)
        total_bid_volume, best_bid_price = self.total_volume_best_price_calc(buy_order_list, 1)

        current_positions = self.position[product]

        for ask_price, ask_vol in sell_order_list:
            if ((ask_price < acc_bid) or ((self.position[product]<0) and (ask_price == acc_bid))) and current_positions < self.position_limit['AMETHYSTS']:
                order_for = min(-ask_vol, self.position_limit['AMETHYSTS'] - current_positions)
                current_positions += order_for
                if order_for >= 0: 
                    orders.append(Order(product, ask_price, order_for))

        undercut_buy = best_bid_price + 1
        undercut_sell = best_ask_price - 1
        bid_pr = min(undercut_buy, acc_bid-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask+1)

        if (current_positions < self.position_limit['AMETHYSTS']) and (self.position[product] < 0):
            num = min(40, self.position_limit['AMETHYSTS'] - current_positions)
            orders.append(Order(product, min(undercut_buy + 1, acc_bid-1), num))
            current_positions += num

        if (current_positions < self.position_limit['AMETHYSTS']) and (self.position[product] > 15):
            num = min(40, self.position_limit['AMETHYSTS'] - current_positions)
            orders.append(Order(product, min(undercut_buy - 1, acc_bid-1), num))
            current_positions += num

        if current_positions < self.position_limit['AMETHYSTS']:
            num = min(40, self.position_limit['AMETHYSTS'] - current_positions)
            orders.append(Order(product, bid_pr, num))
            current_positions += num

        cpos = self.position[product]  # cpos is current position 

        for bid, vol in buy_order_list: 
            if ((bid > acc_ask) or ((self.position[product]>0) and (bid == acc_ask))) and cpos > -self.position_limit['AMETHYSTS']:
                order_for = max(-vol, -self.position_limit['AMETHYSTS']-cpos)
                # Order_for is a negative number denoting how much we will sell
                cpos += order_for
                if order_for <= 0:
                    orders.append(Order(product, bid, order_for))

        if (cpos > -self.position_limit['AMETHYSTS']) and (self.position[product] > 0):
            num = max(-40, -self.position_limit['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell-1, acc_ask+1), num))
            cpos += num

        if (cpos > -self.position_limit['AMETHYSTS']) and (self.position[product] < -15):
            num = max(-40, -self.position_limit['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell+1, acc_ask+1), num))
            cpos += num

        if cpos > -self.position_limit['AMETHYSTS']:
            num = max(-40, -self.position_limit['AMETHYSTS']-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders

    def compute_orders(self, product, order_depth, acc_bid, acc_ask):
        if product == "AMETHYSTS":
            return self.compute_orders_amethysts(product, order_depth, acc_bid, acc_ask)
    
    def run(self, state: TradingState): 
        # Initialize the method output dict as an empty dict
        result = {"GIFT_BASKET":[]}
        amethysts_lb = 10000
        amethysts_ub = 10000

        for product in state.order_depths:
            if product == "AMETHYSTS": 
                order_depth: OrderDepth = state.order_depths[product]
                orders = self.compute_orders(product, order_depth, amethysts_lb, amethysts_ub)
                result[product] = orders

            if product == 'STARFRUIT':
                orders: List[Order] = []
                order_depth: OrderDepth = state.order_depths[product]
                c_ask = list(state.order_depths['STARFRUIT'].sell_orders.keys())
                c_bid = list(state.order_depths['STARFRUIT'].buy_orders.keys())
                c_mid = [(ask + bid)/2 for ask, bid in zip(c_ask, c_bid)]
                c_mid_series = pd.Series(c_mid)
                exp12 = c_mid_series.ewm(span = 55, adjust = False).mean()
                exp26 = c_mid_series.ewm(span = 89, adjust = False).mean()
                macd = exp12 - exp26
                signal = macd.ewm(span = 9, adjust = False).mean()
                # Initialize results
                position_limit = 20
                if product in state.position:
                    quantity_position = state.position[product]
                else: 
                    quantity_position = 0
                
                #Trading Strategies
                if (macd <= signal).any() and -position_limit < quantity_position < position_limit: # Selling logic
                    bid, bid_amount = list(order_depth.buy_orders.items())[0]
                    orders.append(Order('STARFRUIT', bid, -20 - quantity_position))
                #if macd.any() >= 1.5 and -position_limit < quantity_position < position_limit:
                #    bid, bid_amount = list(order_depth.buy_orders.items())[0]
                #    orders.append(Order('STARFRUIT', bid, -20-quantity_position)) # High, sell
                if (macd > signal).any() and -position_limit < quantity_position < position_limit: # Buying logic
                    ask, ask_amount = list(order_depth.sell_orders.items())[0]
                    orders.append(Order('STARFRUIT', ask, 20 - quantity_position))
                #if macd.any() <= 1.4 and -position_limit < quantity_position < position_limit:
                #    ask, ask_amount = list(order_depth.sell_orders.items())[0]
                #    orders.append(Order('STARFRUIT', ask, 20 - quantity_position)) # Low, buy
                result[product] = orders

            if product == "ORCHIDS":
                orders: List[Order] = []
                conversions = 0
                if product in state.position:
                    quantity_position = state.position[product]
                else: 
                    quantity_position = 0

                conversion_obv = state.observations.conversionObservations[product]

                if product in state.own_trades:
                    own_trades = state.own_trades[product]
                else:
                    own_trades = []

                local_ask_list = list(state.order_depths['ORCHIDS'].sell_orders.keys())
                local_bid_list = list(state.order_depths['ORCHIDS'].buy_orders.keys())
                best_local_ask = min(local_ask_list) # min ask price
                best_local_bid = max(local_bid_list) # max bid price 
                spread = (best_local_ask - best_local_bid) / 2
                best_ask_quantity = state.order_depths['ORCHIDS'].sell_orders[best_local_ask] # <0 
                best_bid_quantity = state.order_depths['ORCHIDS'].buy_orders[best_local_bid] # >0 

                foreign_ask_price = conversion_obv.askPrice + conversion_obv.importTariff + conversion_obv.transportFees
                self.foreign_ask.append(foreign_ask_price)

                #arbitrage2: foreign ask < local sell price, we can short sell at local first, then import 
                sell_price = int(best_local_ask - spread)
                print("foreign ask price is", foreign_ask_price)
                print("sell price is", sell_price)
                if quantity_position == 0: 
                    orders.append(Order(product, sell_price, -77)) # we sell at a lower local ask price
                    self.sold_time = state.timestamp
                    self.sold_price = 0
                else:
                    #print("sold time is", self.sold_time)
                    for trades in own_trades:
                        if trades.timestamp == self.sold_time:
                            self.sold_price = trades.price
                    #print("sold.price is", self.sold_price)
                        
                if state.timestamp <= self.sold_time + 200:
                    profit_margin = self.sold_price - foreign_ask_price
                    #print("profit margin is ", profit_margin)
                    if profit_margin >= 0.5:
                        conversions = -quantity_position
                else: 
                    conversions = -quantity_position

                result[product] = orders

        for product in ["CHOCOLATE", "ROSES", "STRAWBERRIES"]:
            ask_price = list(state.order_depths[product].sell_orders.keys())
            bid_price = list(state.order_depths[product].buy_orders.keys())
            mid_price = [(ask + bid)/2 for ask, bid in zip(ask_price, bid_price)]
            mid_series = pd.Series(mid_price)
            exp12 = mid_series.ewm(span = 12, adjust = False).mean()
            exp26 = mid_series.ewm(span = 26, adjust = False).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span = 9, adjust = False).mean()

            # Initialize results
            orders: List[Order] = []
            order_depth: OrderDepth = state.order_depths[product]
            order_depth_gift = state.order_depths["GIFT_BASKET"]
            best_ask_gift = list(order_depth_gift.sell_orders.keys())[0]
            best_bid_gift = list(order_depth_gift.buy_orders.keys())[0]
            gift_mid_price = (best_ask_gift + best_bid_gift) / 2

            best_bid = list(order_depth.buy_orders.keys())[0] 
            best_ask = list(order_depth.sell_orders.keys())[0] 
            best_mid = (best_bid + best_ask) / 2
            # Trading Strategies
            if (macd <= signal).any(): # Selling logic
                quantity_sell = order_depth.buy_orders[best_bid]
                orders.append(Order(product, best_bid, -quantity_sell))
                if product in ["CHOCOLATE", "STRAWBERRIES"]:
                    quantity = math.ceil(quantity_sell * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_ask_gift, quantity))
                elif product == "ROSES":
                    quantity = math.floor(quantity_sell * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_ask_gift, quantity))

            if (macd > signal).any(): # Buying logic
                quantity_buy = order_depth.sell_orders[best_ask]
                orders.append(Order(product, best_ask, -quantity_buy))
                if product in ["CHOCOLATE", "STRAWBERRIES"]:
                    quantity = math.ceil(quantity_buy * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_bid_gift, quantity))
                elif product == "ROSES":
                    quantity = math.floor(quantity_buy * best_mid / gift_mid_price)
                    result["GIFT_BASKET"].append(Order("GIFT_BASKET", best_bid_gift, quantity))

            result[product] = orders


        traderData = "SAMPLE"  # Placeholder value

        return result, conversions, traderData
        


