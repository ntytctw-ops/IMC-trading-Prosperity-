from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import pandas as pd
import collections
from collections import defaultdict
import random
import math
import copy
import numpy as np

empty_dict = {'STARFRUIT' : 0, 'AMETHYSTS' : 0, 'ORCHIDS' : 0, 'CHOCOLATE' : 0, 'STRAWBERRIES': 0, 'ROSES' : 0, 'GIFT_BASKET' : 0}


def def_value():
    return copy.deepcopy(empty_dict)

INF = int(1e9)

class Trader:
    def __init__(self):
        self.ame_ask = []
        self.ame_bid = []
        self.ame_mid = []
    position = copy.deepcopy(empty_dict)
    POSITION_LIMIT = {'STARFRUIT' : 20, 'AMETHYSTS' : 20, 'ORCHIDS' : 100, 'CHOCOLATE' : 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}
    volume_traded = copy.deepcopy(empty_dict)

    person_position = defaultdict(def_value)
    person_actvalof_position = defaultdict(def_value)

    cpnl = defaultdict(lambda : 0)
    starfruit_cache = []
    starfruit_dim = 4
    steps = 0
    cont_buy_basket_unfill = 0
    cont_sell_basket_unfill = 0
    
    halflife_diff = 5
    alpha_diff = 1 - np.exp(-np.log(2)/halflife_diff)

    halflife_price = 5
    alpha_price = 1 - np.exp(-np.log(2)/halflife_price)

    halflife_price_dip = 20
    alpha_price_dip = 1 - np.exp(-np.log(2)/halflife_price_dip)
    
    begin_diff_dip = -INF
    begin_diff_bag = -INF
    begin_bag_price = -INF
    begin_dip_price = -INF

    std = 25
    basket_std = 117
    
    def compute_orders_amethysts(self, product, order_depth, acc_bid, acc_ask):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        cpos = self.position[product]

        mx_with_buy = -1

        for ask, vol in osell.items():
            if ((ask < acc_bid) or ((self.position[product]<0) and (ask == acc_bid))) and cpos < self.POSITION_LIMIT['AMETHYSTS']:
                mx_with_buy = max(mx_with_buy, ask)
                order_for = min(-vol, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        mprice_actual = (best_sell_pr + best_buy_pr)/2
        mprice_ours = (acc_bid+acc_ask)/2

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid-1) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask+1)

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < 0):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy + 1, acc_bid-1), num))
            cpos += num

        if (cpos < self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 15):
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, min(undercut_buy - 1, acc_bid-1), num))
            cpos += num

        if cpos < self.POSITION_LIMIT['AMETHYSTS']:
            num = min(40, self.POSITION_LIMIT['AMETHYSTS'] - cpos)
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product]

        for bid, vol in obuy.items():
            if ((bid > acc_ask) or ((self.position[product]>0) and (bid == acc_ask))) and cpos > -self.POSITION_LIMIT['AMETHYSTS']:
                order_for = max(-vol, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
                # Order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] > 0):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell-1, acc_ask+1), num))
            cpos += num

        if (cpos > -self.POSITION_LIMIT['AMETHYSTS']) and (self.position[product] < -15):
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, max(undercut_sell+1, acc_ask+1), num))
            cpos += num

        if cpos > -self.POSITION_LIMIT['AMETHYSTS']:
            num = max(-40, -self.POSITION_LIMIT['AMETHYSTS']-cpos)
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders


    def compute_orders_regression(self, product, order_depth, acc_bid, acc_ask, LIMIT):
        orders: list[Order] = []

        osell = collections.OrderedDict(sorted(order_depth.sell_orders.items()))
        obuy = collections.OrderedDict(sorted(order_depth.buy_orders.items(), reverse=True))

        sell_vol, best_sell_pr = self.values_extract(osell)
        buy_vol, best_buy_pr = self.values_extract(obuy, 1)

        cpos = self.position[product]

        for ask, vol in osell.items():
            if ((ask <= acc_bid) or ((self.position[product]<0) and (ask == acc_bid+1))) and cpos < LIMIT:
                order_for = min(-vol, LIMIT - cpos)
                cpos += order_for
                assert(order_for >= 0)
                orders.append(Order(product, ask, order_for))

        undercut_buy = best_buy_pr + 1
        undercut_sell = best_sell_pr - 1

        bid_pr = min(undercut_buy, acc_bid) # we will shift this by 1 to beat this price
        sell_pr = max(undercut_sell, acc_ask)

        if cpos < LIMIT:
            num = LIMIT - cpos
            orders.append(Order(product, bid_pr, num))
            cpos += num
        
        cpos = self.position[product]
        

        for bid, vol in obuy.items():
            if ((bid >= acc_ask) or ((self.position[product]>0) and (bid+1 == acc_ask))) and cpos > -LIMIT:
                order_for = max(-vol, -LIMIT-cpos)
                # Order_for is a negative number denoting how much we will sell
                cpos += order_for
                assert(order_for <= 0)
                orders.append(Order(product, bid, order_for))

        if cpos > -LIMIT:
            num = -LIMIT-cpos
            orders.append(Order(product, sell_pr, num))
            cpos += num

        return orders
    
    def run(self, state: TradingState):
        products = ['AMETHYSTS', 'STARFRUIT', 'ORCHIDS', 'CHOCOLATE', 'STRAWBERRIES', 'ROSES', 'GIFT_BASKET']
        for product in products:
            if product == 'AMETHYSTS':
                amethysts_lb = 10000
                amethysts_ub = 10000
                acc_bid = {'AMETHYSTS' : amethysts_lb} # we want to buy at slightly below
                acc_ask = {'AMETHYSTS' : amethysts_ub} # we want to sell at slightly above
                order_depth: OrderDepth = state.order_depths[product]
                orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
                result[product] += orders
            if product == 'STARFRUIT':
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
                result = {}
                if product in state.position:
                    quantity_position = state.position[product]
                else: 
                    quantity_position = 0
                orders: List[Order] = []
                order_depth: OrderDepth = state.order_depths[product]
                traderData = 'STARFRUIT only'
                conversions = 0

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
    
    
        traderData = 'Round3'
        conversions = 0
        return result, conversions, traderData