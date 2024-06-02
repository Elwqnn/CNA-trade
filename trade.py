#!/usr/bin/env python3

##
## EPITECH PROJECT, 2024
## CNA-trade
## File description:
## trade
##

import sys

class Candle:
    def __init__(self, format, intel):
        tmp = intel.split(",")
        self.pair = tmp[format.index("pair")]
        self.date = int(tmp[format.index("date")])
        self.high = float(tmp[format.index("high")])
        self.low = float(tmp[format.index("low")])
        self.open = float(tmp[format.index("open")])
        self.close = float(tmp[format.index("close")])
        self.volume = float(tmp[format.index("volume")])

    def __repr__(self):
        return f"{self.pair} {self.date} {self.close} {self.volume}"

class Chart:
    def __init__(self):
        self.closes = []
        self.highs = []
        self.lows = []

    def add_candle(self, candle: Candle):
        self.closes.append(candle.close)
        self.highs.append(candle.high)
        self.lows.append(candle.low)

class BotState:
    def __init__(self):
        self.maxTimeBank = 0
        self.timePerMove = 1
        self.candleFormat = []
        self.transactionFee = 0.1
        self.date = 0
        self.stacks = {}
        self.charts = {}

    def update_chart(self, pair: str, new_candle_str: str):
        if pair not in self.charts:
            self.charts[pair] = Chart()
        new_candle_obj = Candle(self.candleFormat, new_candle_str)
        self.charts[pair].add_candle(new_candle_obj)

    def update_stack(self, key: str, value: float):
        self.stacks[key] = value

    def update_settings(self, key: str, value: str):
        if key == "timebank":
            self.maxTimeBank = int(value)
        elif key == "time_per_move":
            self.timePerMove = int(value)
        elif key == "candle_format":
            self.candleFormat = value.split(",")
        elif key == "transaction_fee_percent":
            self.transactionFee = float(value)

    def update_game(self, key: str, value: str):
        if key == "next_candles":
            new_candles = value.split(";")
            self.date = int(new_candles[0].split(",")[1])
            for candle_str in new_candles:
                candle_infos = candle_str.strip().split(",")
                self.update_chart(candle_infos[0], candle_str)
        elif key == "stacks":
            new_stacks = value.split(",")
            for stack_str in new_stacks:
                stack_infos = stack_str.strip().split(":")
                self.update_stack(stack_infos[0], float(stack_infos[1]))

class Bot:
    def __init__(self):
        self.botState = BotState()

    def run(self):
        while True:
            reading = input()
            if reading:
                self.parse(reading)

    def parse(self, info: str):
        info_parts = info.split(" ")
        if info_parts[0] == "settings":
            self.botState.update_settings(info_parts[1], info_parts[2])
        elif info_parts[0] == "update":
            if info_parts[1] == "game":
                self.botState.update_game(info_parts[2], info_parts[3])
        elif info_parts[0] == "action":
            self.act()

    def act(self):
        usdt = self.botState.stacks.get("USDT", 0)
        btc = self.botState.stacks.get("BTC", 0)
        chart = self.botState.charts.get("USDT_BTC", Chart())

        if len(chart.closes) < 30:
            print("no_moves", flush=True)
            return

        short_ema = self.get_ema(chart.closes, 5)
        mid_ema = self.get_ema(chart.closes, 12)
        long_ema = self.get_ema(chart.closes, 26)
        macd, signal = self.get_macd(chart.closes)
        rsi = self.get_rsi(chart.closes)
        bollinger_upper, bollinger_lower = self.get_bollinger_bands(chart.closes)

        current_closing_price = chart.closes[-1]
        affordable = usdt / current_closing_price

        if (short_ema > mid_ema > long_ema and macd > signal and rsi < 70 and
            current_closing_price < bollinger_upper):
            amount_to_buy = 0.5 * affordable * (1 - self.botState.transactionFee / 100)
            if amount_to_buy > 0:
                sys.stderr.write(f"===== BUYING =====\n")
                sys.stderr.write(f"current stacks: {self.botState.stacks}\n")
                sys.stderr.write(f"amount: {amount_to_buy} USDT\n")
                print(f'buy USDT_BTC {amount_to_buy}', flush=True)
                return
        elif (short_ema < mid_ema < long_ema and macd < signal and rsi > 30 and
              current_closing_price > bollinger_lower):
            if btc > 0:
                sys.stderr.write(f"===== SELLING =====\n")
                sys.stderr.write(f"current stacks: {self.botState.stacks}\n")
                sys.stderr.write(f"amount: {btc} BTC\n")
                print(f'sell USDT_BTC {btc}', flush=True)
                return
        print("no_moves", flush=True)

    @staticmethod
    def get_ema(prices, window):
        alpha = 2 / (window + 1)
        ema = [sum(prices[:window]) / window]
        for price in prices[window:]:
            ema.append((price - ema[-1]) * alpha + ema[-1])
        return ema[-1]

    @staticmethod
    def get_macd(prices, short_window=12, long_window=26, signal_window=9):
        short_ema = Bot.get_ema(prices, short_window)
        long_ema = Bot.get_ema(prices, long_window)
        macd = short_ema - long_ema
        signal = Bot.get_ema([macd], signal_window)
        return macd, signal

    @staticmethod
    def get_rsi(prices, period=14):
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        seed = deltas[:period + 1]
        up = sum(val for val in seed if val >= 0) / period
        down = -sum(val for val in seed if val < 0) / period
        rs = up / down
        rsi = [0] * len(prices)
        rsi[period] = 100. - 100. / (1. + rs)

        for i in range(period + 1, len(prices)):
            delta = prices[i] - prices[i - 1]
            if delta > 0:
                up_val = delta
                down_val = 0.
            else:
                up_val = 0.
                down_val = -delta

            up = (up * (period - 1) + up_val) / period
            down = (down * (period - 1) + down_val) / period

            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)

        return rsi[-1]

    @staticmethod
    def get_bollinger_bands(prices, window=15, num_std_dev=1.5):
        sma = sum(prices[-window:]) / window
        std_dev = (sum((x - sma) ** 2 for x in prices[-window:]) / window) ** 0.5
        upper_band = sma + (std_dev * num_std_dev)
        lower_band = sma - (std_dev * num_std_dev)
        return upper_band, lower_band

if __name__ == "__main__":
    mybot = Bot()
    mybot.run()
