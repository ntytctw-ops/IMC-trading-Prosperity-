from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    def __init__(self):
        self.starfruit_trend_window = 5
        self.amethysts_mean_window = 10
        self.position_limits = {"AMETHYSTS": 50, "STARFRUIT": 50}
        # Minimum volume to consider for trading to ensure liquidity
        self.minimum_liquidity_volume = 10
    
    def run(self, state: TradingState):
        for product in state.products:
            # Calculate necessary statistics for each strategy
            mid_prices = [trade.mid_price for trade in state.trades if trade.product == product]
            avg_volumes = [trade.volume for trade in state.trades if trade.product == product]
            avg_volume = sum(avg_volumes) / len(avg_volumes) if avg_volumes else 0
            
            if product == "STARFRUIT":
                # Trend Following Strategy for STARFRUIT
                if len(mid_prices) > self.starfruit_trend_window and avg_volume > self.minimum_liquidity_volume:
                    trend = self.calculate_trend(mid_prices, self.starfruit_trend_window)
                    self.apply_trend_following_strategy(state, product, trend, avg_volume)
            elif product == "AMETHYSTS":
                # Mean Reversion Strategy for AMETHYSTS
                if len(mid_prices) > self.amethysts_mean_window and avg_volume > self.minimum_liquidity_volume:
                    deviation_from_mean = self.calculate_deviation_from_mean(mid_prices, self.amethysts_mean_window)
                    self.apply_mean_reversion_strategy(state, product, deviation_from_mean, avg_volume)
    
    def calculate_trend(self, prices, window):
        return prices[-1] - prices[-window]
    
    def apply_trend_following_strategy(self, state, product, trend, avg_volume):
        position = state.get_position(product)
        quantity = min(self.position_limits[product] - abs(position), avg_volume // 2)  # Adjust quantity based on available volume
        if trend > 0 and position < self.position_limits[product]:
            self.send_order(state, product, "BUY", quantity)
        elif trend < 0 and position > -self.position_limits[product]:
            self.send_order(state, product, "SELL", quantity)
    
    def calculate_deviation_from_mean(self, prices, window):
        mean_price = sum(prices[-window:]) / window
        return prices[-1] - mean_price
    
    def apply_mean_reversion_strategy(self, state, product, deviation, avg_volume):
        position = state.get_position(product)
        quantity = min(self.position_limits[product] - abs(position), avg_volume // 2)  # Adjust quantity based on available volume
        if deviation < 0 and position < self.position_limits[product]:
            self.send_order(state, product, "BUY", quantity)
        elif deviation > 0 and position > -self.position_limits[product]:
            self.send_order(state, product, "SELL", quantity)
    
    def send_order(self, state, product, action, quantity):
        # Example implementation. This needs to be adjusted to fit the actual order sending mechanism.
        print(f"Sending {action} order for {quantity} units of {product}.")
