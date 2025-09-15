from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import collections
from collections import defaultdict
import random
import math
import copy
import numpy as np
import statistics

empty_dict = {'STARFRUIT' : 0, 'AMETHYSTS' : 0}


def def_value():
    return copy.deepcopy(empty_dict)

INF = int(1e9)

class Trader:
    def __init__(self):
        # Initialize with pre-defined coefficients and intercept
        self.intercept = 693.3200659097004
        self.coef_sunlight = 0.04013674
        self.coef_humidity = 3.77920383
        self.local_ask = []
        self.local_bid = []
        self.local_mid = []
        self.foreign_ask = []
        self.foreign_ask_amount = []
        self.foreign_bid = []
        self.foreign_bid_amount = []
        self.timestamp = []
        self.prices_history = {"STARFRUIT": [], "AMETHYSTS": [], "ORCHIDS": []}
        self.spread = {"STARFRUIT": [], "AMETHYSTS": [], "ORCHIDS": []}
        self.position_limit = {"STARFRUIT": 20, "AMETHYSTS": 20, "ORCHIDS": 100}
        self.humidity_obs = []
        self.sunlight_obs = []
        self.avg_window = 15
        self.profitted_trade_index = []
        self.buy_execution_count = 0
        self.execution_count = 1
        self.arbitrage_time = []
        self.total_arbitrage_quantity = 0

    def predict_orchid_price(self, sunlight, humidity):
        # Manually calculate the predicted orchid price
        return self.intercept + self.coef_sunlight * sunlight + self.coef_humidity * humidity
    
    def orchid_price_trend(self, current_sunlight, current_humidity, delta_humidity, delta_sunlight):
        good_humidity = 60 <= current_humidity <= 80
        good_sun = current_sunlight >= 2500
        if not good_sun and not good_humidity:
            return 2.0 * delta_humidity - 5.288e-03 * delta_sunlight
        elif good_humidity and not good_sun:
            return 0.5 * delta_humidity + 3.563e-02 * delta_sunlight
        elif not good_humidity and good_sun:
            return 1.3 * delta_humidity + 3.973e-02 * delta_sunlight



    position = copy.deepcopy(empty_dict)
    POSITION_LIMIT = {'STARFRUIT' : 20, 'AMETHYSTS' : 20}
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

    def calc_next_price_starfruit(self):
        # Starfruit cache stores price from 1 day ago, current day resp
        # Here we use mid price as requested
        coef = [-0.01869561,  0.0455032 ,  0.16316049,  0.8090892]
        intercept = 4.481696494462085
        nxt_price = intercept
        for i, val in enumerate(self.starfruit_cache):
            nxt_price += val * coef[i]

        return int(round(nxt_price))

    def values_extract(self, order_dict, buy=0):
        tot_vol = 0
        best_val = -1
        mxvol = -1

        for ask, vol in order_dict.items():
            if(buy==0):
                vol *= -1
            tot_vol += vol
            if tot_vol > mxvol:
                mxvol = vol
                best_val = ask
        
        return tot_vol, best_val
    

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
    


    def compute_orders(self, product, order_depth, acc_bid, acc_ask):

        if product == "AMETHYSTS":
            return self.compute_orders_amethysts(product, order_depth, acc_bid, acc_ask)
        if product == "STARFRUIT":
            return self.compute_orders_regression(product, order_depth, acc_bid, acc_ask, self.POSITION_LIMIT[product])
        
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {'AMETHYSTS' : [], 'STARFRUIT' : [], 'ORCHIDS': []}

        # Iterate over all the keys (the available products) contained in the order dephts
        for key, val in state.position.items():
            self.position[key] = val
        print()
        for key, val in self.position.items():
            print(f'{key} position: {val}')

        timestamp = state.timestamp

        if len(self.starfruit_cache) == self.starfruit_dim:
            self.starfruit_cache.pop(0)

        _, bs_starfruit = self.values_extract(collections.OrderedDict(sorted(state.order_depths['STARFRUIT'].sell_orders.items())))
        _, bb_starfruit = self.values_extract(collections.OrderedDict(sorted(state.order_depths['STARFRUIT'].buy_orders.items(), reverse=True)), 1)

        self.starfruit_cache.append((bs_starfruit+bb_starfruit)/2)

        INF = 1e9
    
        starfruit_lb = -INF
        starfruit_ub = INF

        if len(self.starfruit_cache) == self.starfruit_dim:
            starfruit_lb = self.calc_next_price_starfruit()-1
            starfruit_ub = self.calc_next_price_starfruit()+1

        amethysts_lb = 10000
        amethysts_ub = 10000


        acc_bid = {'AMETHYSTS' : amethysts_lb, 'STARFRUIT' : starfruit_lb} # we want to buy at slightly below
        acc_ask = {'AMETHYSTS' : amethysts_ub, 'STARFRUIT' : starfruit_ub} # we want to sell at slightly above

        self.steps += 1

        for product in state.market_trades.keys():
            if product != "ORCHIDS":
                for trade in state.market_trades[product]:
                    if trade.buyer == trade.seller:
                        continue
                    self.person_position[trade.buyer][product] = 1.5
                    self.person_position[trade.seller][product] = -1.5
                    self.person_actvalof_position[trade.buyer][product] += trade.quantity
                    self.person_actvalof_position[trade.seller][product] += -trade.quantity

        for product in ['AMETHYSTS', 'STARFRUIT']:
            order_depth: OrderDepth = state.order_depths[product]
            orders = self.compute_orders(product, order_depth, acc_bid[product], acc_ask[product])
            result[product] += orders

        for product in state.own_trades.keys():
            if product != "ORCHIDS": 
                for trade in state.own_trades[product]:
                    if trade.timestamp != state.timestamp-100:
                        continue
                    self.volume_traded[product] += abs(trade.quantity)
                    if trade.buyer == "SUBMISSION":
                        self.cpnl[product] -= trade.quantity * trade.price
                    else:
                        self.cpnl[product] += trade.quantity * trade.price

        totpnl = 0

        for product in state.order_depths.keys():
            if product != "ORCHIDS":
                settled_pnl = 0
                best_sell = min(state.order_depths[product].sell_orders.keys())
                best_buy = max(state.order_depths[product].buy_orders.keys())

                if self.position[product] < 0:
                    settled_pnl += self.position[product] * best_buy
                else:
                    settled_pnl += self.position[product] * best_sell
                totpnl += settled_pnl + self.cpnl[product]
                print(f"For product {product}, {settled_pnl + self.cpnl[product]}, {(settled_pnl+self.cpnl[product])/(self.volume_traded[product]+1e-20)}")

        #ORCHIDS trading 
        product = "ORCHIDS"
        conversion_obv = state.observations.conversionObservations[product]
        current_sunlight = conversion_obv.sunlight
        current_humidity = conversion_obv.humidity
        # Current foreign market prices
        self.foreign_ask.append(conversion_obv.askPrice)
        self.foreign_bid.append(conversion_obv.bidPrice)
        foreign_ask_price = np.mean(self.foreign_ask)
        foreign_bid_price = np.mean(self.foreign_bid)
        # Current local market prices
        local_ask = list(state.order_depths['ORCHIDS'].sell_orders.keys())
        local_bid = list(state.order_depths['ORCHIDS'].buy_orders.keys())
        current_local_ask, local_ask_amount = list(state.order_depths['ORCHIDS'].sell_orders.items())[0]
        current_local_bid, local_bid_amount = list(state.order_depths['ORCHIDS'].buy_orders.items())[0]  
        local_mid = (local_ask[0] + local_bid[0])/2
        self.local_mid.append(local_mid)
        local_mid_price = np.mean(self.local_mid)
        high_local_mid = local_mid_price * 1.01
        low_local_mid = local_mid_price * 0.99
        # Calculate pivot points, S1, S2, R1 for local
        pivot_point_local_mid = int((high_local_mid + low_local_mid + local_mid)/3)
        support_local = int(2 * pivot_point_local_mid - high_local_mid)
        resistance_local = int(2 * pivot_point_local_mid - low_local_mid)
        support_local_2 = int(pivot_point_local_mid - (high_local_mid - low_local_mid))
        high_foreign_ask = foreign_ask_price * 1.01 
        low_foreign_ask = foreign_ask_price * 0.99
        high_foreign_bid = foreign_bid_price * 1.01
        low_foreign_bid = foreign_bid_price * 0.99
        # Calculate pivot points, S1, R1, S2 for imports & exports
        pivot_point_import = int((high_foreign_ask + low_foreign_ask + local_ask[0])/3)
        support_import = int(2 * pivot_point_import - high_foreign_ask)
        support_import_2 = int(pivot_point_import - (high_foreign_ask - low_foreign_ask))
        pivot_point_export = int((high_foreign_bid + low_foreign_bid + local_bid[0])/3)
        resistance_export = int(2 * pivot_point_export - low_foreign_bid)
        print(support_local, resistance_local, pivot_point_export, pivot_point_import, support_import, resistance_export)
        # Predict the local price based on environmental conditions
        predicted_local_price = self.predict_orchid_price(current_sunlight, current_humidity)
        # Predict the foreign import price
        import_tariff_mean = np.mean(conversion_obv.importTariff)
        trans_mean = np.mean(conversion_obv.transportFees)
        predicted_foreign_import = predicted_local_price - import_tariff_mean - trans_mean
        # Predict the foreign export price
        export_tariff_mean = np.mean(conversion_obv.exportTariff)
        predicted_foreign_export = predicted_local_price - export_tariff_mean  - trans_mean
        
        # Current local market prices
        current_spread = current_local_ask - current_local_bid
        current_mid_price = (current_local_ask + current_local_bid) * 0.5

        self.prices_history[product].append(current_mid_price)
        self.spread[product].append(current_spread)
        self.humidity_obs.append(current_humidity)
        self.sunlight_obs.append(current_sunlight)

        if len(self.prices_history[product]) > self.avg_window+2: # this value here should be the same as the avg window 
            self.prices_history[product].pop(0)
        if len(self.spread[product]) > self.avg_window+2:
            self.spread[product].pop(0)
        if len(self.humidity_obs) > 20:
            self.humidity_obs.pop(0)
        if len(self.sunlight_obs) > 20:
            self.sunlight_obs.pop(0)

        # Predict the local price based on environmental conditions
        if state.timestamp > self.avg_window * 100: 
            avg_spread = statistics.mean(self.spread[product][-(self.avg_window+1):-1])
            avg_mid_price = statistics.mean(self.prices_history[product][-(self.avg_window+1):-1])
        else: 
            avg_spread = statistics.mean(self.spread[product])
            avg_mid_price = statistics.mean(self.prices_history[product])
        if len(self.humidity_obs) >= 11:
            delta_humidity = current_humidity - self.humidity_obs[-2]
            delta_sunlight = current_sunlight - self.sunlight_obs[-5]
        else:
            delta_humidity = 0.01
            delta_sunlight = 0.6

        predicted_orchid_price = avg_mid_price + self.orchid_price_trend(current_sunlight, current_humidity, delta_humidity, delta_sunlight)
        predicted_local_ask = predicted_orchid_price + avg_spread / 2
        predicted_local_bid = predicted_orchid_price - avg_spread / 2
        
        # Initialize the results dictionary
        orders: List[Order] = []
        traderData = f'Predicted local price: {predicted_orchid_price:.2f}'
        conversions = 0

        for bid_price, bid_quantity in state.order_depths['ORCHIDS'].buy_orders.items():
            if conversion_obv.askPrice < bid_price - 1: #arbitrage opportunity
                orders.append(Order('ORCHIDS', bid_price - 1, -bid_quantity+50))  # Implicit sell
                self.arbitrage_time.append(state.timestamp)
 
        if product in state.own_trades:
            for index,trade in enumerate(state.own_trades[product]):
                if index not in self.profitted_trade_index and trade.timestamp in self.arbitrage_time:
                    conversions += trade.quantity
                    self.profitted_trade_index.append(index)
                if index not in self.profitted_trade_index and trade.timestamp not in self.arbitrage_time:
                    if trade.buyer == "SUBMISSION" and trade.price < current_local_bid - 1.5*avg_spread:
                        orders.append(Order('ORCHIDS', current_local_bid, -trade.quantity))  # Implicit sell
                        self.profitted_trade_index.append(index)
                        #self.profitted_trade_index.append(len(self.profitted_trade_index))
                        self.execution_count += 1
                    if trade.seller == "SUBMISSION" and trade.price > current_local_ask + 1.5*avg_spread:
                        orders.append(Order('ORCHIDS', current_local_ask, trade.quantity))  # Implicit buy
                        self.profitted_trade_index.append(index) 
                        #self.profitted_trade_index.append(len(self.profitted_trade_index))
                        self.execution_count += 1
        '''if self.execution_count == 1:
            if predicted_local_ask > current_local_ask:
                self.buy_execution_count += 1 
            if predicted_local_bid < current_local_bid:
                orders.append(Order('ORCHIDS', current_local_bid, -local_bid_amount))  # Implicit sell
                self.execution_count == 0   
            if self.buy_execution_count == 2: 
                orders.append(Order('ORCHIDS', current_local_ask, -local_ask_amount))  # Implicit buy
                self.buy_execution_count == 0 
                self.execution_count == 0  '''

        # Local trading decisions
        #if predicted_local_price >= current_local_ask:
        #    orders.append(Order('ORCHIDS', current_local_ask, 1))  # Implicit buy

        if pivot_point_export <= predicted_foreign_export <= resistance_export:
            conversions -= 10 # Overseas sell
            #time = self.timestamp.append(state.timestamp)
            #if time[-1] + 1000 == state.timestamp and pivot_point_export > predicted_foreign_export > resistance_export:
            #    conversions -= 2
            if predicted_foreign_export > resistance_export:
                conversions -= 60
        if predicted_local_price <= current_local_bid:
            orders.append(Order('ORCHIDS', current_local_bid, -2)) # Implict sell
        if support_import <= predicted_foreign_import < pivot_point_import:
            conversions += 100 # Overseas buy
        if support_import_2 <= predicted_foreign_export < support_import:
            conversions += 100
                
        result[product] = orders
        
        traderData = "SAMPLE"  # Placeholder value
        
        return result, conversions, traderData