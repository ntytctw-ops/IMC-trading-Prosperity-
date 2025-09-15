from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
import statistics

class Trader:
    def __init__(self):
        self.foreign_ask = []
        self.foreign_bid = []
        self.local_mid_history = []
        self.want_to_export_quantity = 0
        self.want_to_export = 0
        self.want_to_import_quantity = 0
        self.want_to_import = 0

    def run(self, state: TradingState):
        result = {}
        product = "ORCHIDS"
        
        conversion_obv = state.observations.conversionObservations[product]
        local_ask_list = list(state.order_depths['ORCHIDS'].sell_orders.keys())
        local_bid_list = list(state.order_depths['ORCHIDS'].buy_orders.keys())
        local_mid = (local_ask_list[0] + local_bid_list[0])/2
        self.foreign_ask.append(conversion_obv.askPrice + conversion_obv.importTariff + conversion_obv.transportFees)
        self.foreign_bid.append(conversion_obv.bidPrice - conversion_obv.exportTariff - conversion_obv.transportFees)
        self.local_mid_history.append(local_mid)

        historical_local_mid_max, historical_local_mid_min = max(self.local_mid_history), min(self.local_mid_history)
        highest_local_mid, lowest_local_mid = historical_local_mid_max * 1.01, historical_local_mid_min * 0.99
        pivot_point_local_mid = (highest_local_mid + lowest_local_mid + local_mid) / 3 

        historical_max_foreign_ask, historical_max_foreign_bid = max(self.foreign_ask), max(self.foreign_bid)
        historical_min_foreign_ask, historical_min_foreign_bid = min(self.foreign_ask), min(self.foreign_bid)
        

        highest_foreign_ask , highest_foreign_bid = historical_max_foreign_ask * 1.01, historical_max_foreign_bid * 1.01
        lowest_foreign_ask, lowest_foreign_bid = historical_min_foreign_ask * 0.99, historical_min_foreign_bid * 0.99

        pivot_point_import = (highest_foreign_ask + lowest_foreign_ask + local_ask_list[0])/3
        pivot_point_export = (highest_foreign_bid + lowest_foreign_bid + local_bid_list[0])/3
        support_import = 2 * pivot_point_import - highest_foreign_ask  
        support_import_2 = pivot_point_import - (highest_foreign_ask - lowest_foreign_ask)
        resistance_export = 2 * pivot_point_export - lowest_foreign_bid
        support_export = 2 * pivot_point_export - highest_foreign_bid
        support_export_2 = pivot_point_export - (highest_foreign_bid - lowest_foreign_bid)
        resistance_import = 2 * pivot_point_import - lowest_foreign_ask
       
        # Initialize the results dictionary
        orders: List[Order] = []
        conversions = 0
        if product in state.position:
            quantity_position = state.position[product]
        else: 
            quantity_position = 0

        print(quantity_position)
        
        local_best_ask = local_ask_list[0]
        best_ask_quantity = state.order_depths['ORCHIDS'].sell_orders[local_best_ask] #<0
        local_best_bid = local_bid_list[0]
        best_bid_quantity = state.order_depths['ORCHIDS'].buy_orders[local_best_bid] #>0







        if -10 <= quantity_position <= 10 and self.want_to_export == 0 and self.want_to_import == 0:
            if support_export <= conversion_obv.bidPrice <= pivot_point_export: # want to import
                self.want_to_export_quantity = min(best_bid_quantity, 10) #>0
                orders.append(Order("ORCHIDS", local_best_bid, -self.want_to_export_quantity)) # so want to create a short position
                self.want_to_export = 1
            if pivot_point_import <= conversion_obv.askPrice <= resistance_import:  # want to export 
                self.want_to_import_quantity = min(-best_ask_quantity, 10)
                orders.append(Order("ORCHIDS", local_best_ask, self.want_to_import_quantity)) # so want to create a long position
                self.want_to_import = 1
                
        if self.want_to_export == 1 or self.want_to_export == 2: 
            if self.want_to_export == 2:
               self.want_to_export = 0
            conversions = -quantity_position # we import first, then want to export 
            if self.want_to_export == 1: 
                if pivot_point_export <= conversion_obv.bidPrice <= resistance_export:
                    orders.append(Order("ORCHIDS", local_best_ask, min(int(0.75*self.want_to_export_quantity),-best_ask_quantity))) #so want to create a long position
                    self.want_to_export = 2
                if conversion_obv.bidPrice > resistance_export:
                    orders.append(Order("ORCHIDS", local_best_ask, min(int(0.25*self.want_to_export_quantity),-best_ask_quantity))) # want a larger long position
                    self.want_to_export = 2
            
        
        if self.want_to_import == 1 or self.want_to_import == 2:
            if self.want_to_import == 2:
               self.want_to_import = 0 
            conversions = -quantity_position  # we export first, then want to import 
            if self.want_to_import == 1:
                if support_import <= conversion_obv.askPrice <= pivot_point_import: 
                    quantity = min(self.want_to_import_quantity, best_bid_quantity)
                    orders.append(Order("ORCHIDS", local_best_bid, -quantity)) # we want to create a short position to import
                    self.want_to_import = 2
                if conversion_obv.askPrice < support_import:
                    quantity = min(self.want_to_import_quantity, best_bid_quantity)
                    orders.append(Order("ORCHIDS", local_best_bid, -quantity)) # we want to create a short position to import
                    self.want_to_import = 2
            
            
        # local strategy 
        '''if pivot_point_local_mid >= local_best_ask: # we buy here 
            orders.append(Order("ORCHIDS", local_best_ask, -best_ask_quantity)) # buy 
        if pivot_point_local_mid <= local_best_bid: # we sell here 
            orders.append(Order("ORCHIDS", local_best_bid, -best_bid_quantity)) # sell 
        '''
        result[product] = orders
        
        traderData = "SAMPLE"  # Placeholder value

        print("Conversions = ", conversions)
        if product in state.position:
            print("Position is", state.position[product])
        print("want to export", self.want_to_export)
        print("want to import", self.want_to_import)
        
        return result, conversions, traderData