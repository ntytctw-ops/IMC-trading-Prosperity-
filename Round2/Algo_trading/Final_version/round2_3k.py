from typing import List
from datamodel import TradingState, Order, ConversionObservation
import string
import numpy as np

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

   
    def predict_orchid_price(self, sunlight, humidity):
        # Manually calculate the predicted orchid price
        return self.intercept + self.coef_sunlight * sunlight + self.coef_humidity * humidity
    
    def run(self, state: TradingState):
        # Extract current market and environmental data
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
        # Initialize the results dictionary
        result = {}
        orders: List[Order] = []
        traderData = f'Predicted local price: {predicted_local_price:.2f}'
        conversions = 0

        # Local trading decisions
        #if predicted_local_price >= current_local_ask:
        #    orders.append(Order('ORCHIDS', current_local_ask, 1))  # Implicit buy
        if pivot_point_export <= predicted_foreign_export <= resistance_export:
            conversions -= 10 # Overseas sell
            #time = self.timestamp.append(state.timestamp)
            #if time[-1] + 1000 == state.timestamp and pivot_point_export > predicted_foreign_export > resistance_export:
            #    conversions -= 2
            if predicted_foreign_export > resistance_export:
                conversions -= 8
        if predicted_local_price <= current_local_bid:
            orders.append(Order('ORCHIDS', current_local_bid, -10)) # Implict sell
        if support_import <= predicted_foreign_import < pivot_point_import:
            conversions += 10 # Overseas buy
        if support_import_2 <= predicted_foreign_export < support_import:
            conversions += 30

        

        result[product] = orders
        # Return the final results, conversion values, and any trader-specific data
        return result, conversions, traderData
