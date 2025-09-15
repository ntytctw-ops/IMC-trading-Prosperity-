from typing import List
from datamodel import TradingState, Order, ConversionObservation
import string
import statistics

class Trader:
    def __init__(self):
        # Initialize with pre-defined coefficients and intercept
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

    def orchid_price_trend(self, current_sunlight, current_humidity, delta_humidity, delta_sunlight):
        good_humidity = 60 <= current_humidity <= 80
        good_sun = current_sunlight >= 2500
        if not good_sun and not good_humidity:
            return 2.0 * delta_humidity - 5.288e-03 * delta_sunlight
        elif good_humidity and not good_sun:
            return 0.5 * delta_humidity + 3.563e-02 * delta_sunlight
        elif not good_humidity and good_sun:
            return 1.3 * delta_humidity + 3.973e-02 * delta_sunlight
        

    def run(self, state: TradingState):
        # Extract current market and environmental data
        product = "ORCHIDS"
        conversion_obv = state.observations.conversionObservations[product]
        current_sunlight = conversion_obv.sunlight
        current_humidity = conversion_obv.humidity
        # Current local market prices
        current_local_ask, local_ask_amount = list(state.order_depths['ORCHIDS'].sell_orders.items())[0] 
        current_local_bid, local_bid_amount = list(state.order_depths['ORCHIDS'].buy_orders.items())[0] 
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
        result = {}
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
        if self.execution_count == 1:
            if predicted_local_ask > current_local_ask:
                self.buy_execution_count += 1 
            if predicted_local_bid < current_local_bid:
                orders.append(Order('ORCHIDS', current_local_bid, -local_bid_amount))  # Implicit sell
                self.execution_count == 0   
            if self.buy_execution_count == 2: 
                orders.append(Order('ORCHIDS', current_local_ask, -local_ask_amount))  # Implicit buy
                self.buy_execution_count == 0 
                self.execution_count == 0   



        result[product] = orders


        # Return the final results, conversion values, and any trader-specific data
        return result, conversions, traderData
