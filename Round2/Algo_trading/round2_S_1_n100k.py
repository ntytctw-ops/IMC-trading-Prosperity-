from typing import List
from datamodel import TradingState, Order, ConversionObservation
import string

class Trader:
    def __init__(self):
        # Initialize with pre-defined coefficients and intercept
        self.intercept = 693.3200659097004
        self.coef_sunlight = 0.04013674
        self.coef_humidity = 3.77920383

    def predict_orchid_price(self, sunlight, humidity):
        # Manually calculate the predicted orchid price
        return self.intercept + self.coef_sunlight * sunlight + self.coef_humidity * humidity

    def run(self, state: TradingState):
        # Extract current market and environmental data
        product = "ORCHIDS"
        conversion_obv = state.observations.conversionObservations[product]
        current_sunlight = conversion_obv.sunlight
        current_humidity = conversion_obv.humidity
        # Current local market prices
        current_local_ask, local_ask_amount = list(state.order_depths['ORCHIDS'].sell_orders.items())[0] 
        current_local_bid, local_bid_amount = list(state.order_depths['ORCHIDS'].buy_orders.items())[0] 
        mid_price = (current_local_bid+current_local_ask)/2
        # Predict the local price based on environmental conditions
        predicted_local_price = self.predict_orchid_price(current_sunlight, current_humidity)
        
        # Initialize the results dictionary
        result = {}
        orders: List[Order] = []
        traderData = f'Predicted local price: {predicted_local_price:.2f}'
        conversions = 0

        # Local trading decisions
        if predicted_local_price < current_local_ask:
            orders.append(Order('ORCHIDS', current_local_bid, -local_bid_amount))  # Implicit sell
        if predicted_local_price > current_local_bid:
            orders.append(Order('ORCHIDS', current_local_ask, -local_ask_amount))  # Implicit buy



        # Check conversion observations for inter-island trade
        adjusted_export_price = conversion_obv.bidPrice + conversion_obv.transportFees + conversion_obv.exportTariff
        adjusted_import_price = conversion_obv.askPrice + conversion_obv.transportFees + conversion_obv.importTariff

        # Inter-island trading decisions
        '''if adjusted_export_price > conversion_obv.bidPrice: 
            conversions -= 10  # Reflect exported amount
        if adjusted_import_price < predicted_local_price:
            conversions += 10  # Reflect imported amount'''

        result[product] = orders

        # Return the final results, conversion values, and any trader-specific data
        return result, conversions, traderData
