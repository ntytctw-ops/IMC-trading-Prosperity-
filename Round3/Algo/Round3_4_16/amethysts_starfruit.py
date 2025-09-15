from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import math 

class Trader:
    def __init__(self):
        self.position = {'STARFRUIT' : 0, 'AMETHYSTS' : 0}
        self.position_limit = {"STARFRUIT": 20, "AMETHYSTS": 20, "ORCHIDS": 100}

        self.steps = 0

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
        result = {}

        
        self.starfruit_cache.append((best_ask_starfruit+best_bid_starfruit) / 2)

        starfruit_lb = -math.inf
        starfruit_ub = math.inf

        if len(self.starfruit_cache) == self.starfruit_dim:
            starfruit_lb = self.calc_next_price_starfruit()-1
            starfruit_ub = self.calc_next_price_starfruit()+1

        amethysts_lb = 10000
        amethysts_ub = 10000

        acc_bid = {'AMETHYSTS' : amethysts_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : amethysts_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above

        self.steps += 1

        for product in ['AMETHYSTS', 'STARFRUIT']:
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            result[product] += orders

        traderData = "SAMPLE"  # Placeholder value

        conversions = 0  # Placeholder value

        return result, conversions, traderData
        


