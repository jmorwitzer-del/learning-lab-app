import datetime
from utils.alpha_live import live_divergence_signal


class BotEngine:
    """
    Core trading bot engine (simulation mode).
    Handles:
      - Live signal intake
      - Entry/exit logic
      - Logging
      - Broker abstraction (IBKR / Alpaca)
    """

    def __init__(self, base_capital_usd=65):
        self.position = None          # "LONG", "SHORT", or None
        self.last_trade = None        # last executed trade description
        self.log = []                 # recent log entries
        self.broker = None            # assigned broker connector
        self.base_capital_usd = base_capital_usd  # e.g. ~65 USD from 100 AUD

    def set_broker(self, broker_name):
        """Assign a broker connector (simulation mode)."""
        if broker_name == "Interactive Brokers (IBKR)":
            from utils.brokers.ibkr import IBKRBroker
            self.broker = IBKRBroker()
            self._log("Broker set to IBKR (simulation mode).")
        elif broker_name == "Alpaca":
            from utils.brokers.alpaca import AlpacaBroker
            self.broker = AlpacaBroker()
            self._log("Broker set to Alpaca (simulation mode).")
        else:
            self.broker = None
            self._log("No broker selected.")

    def get_live_signal(self):
        """Fetch the current live divergence signal."""
        return live_divergence_signal()

    def should_enter(self, signal):
        """Entry logic: only enter if no position is open."""
        if self.position is None and signal in ["LONG", "SHORT"]:
            return True
        return False

    def should_exit(self):
        """Exit logic: always exit at market close if a position is open."""
        return self.position is not None

    def _log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.log.append(entry)
        self.last_trade = entry

    def _estimate_quantity(self, price):
        """
        Estimate fractional quantity based on base_capital_usd.
        For example, with 65 USD and SPY at 450, quantity ≈ 0.14.
        """
        if price <= 0:
            return 0
        qty = self.base_capital_usd / price
        return round(qty, 4)

    def enter_trade(self, signal, price):
        """Simulate entering a trade and (optionally) sending to broker."""
        qty = self._estimate_quantity(price)
        self.position = signal

        broker_msg = None
        if self.broker is not None:
            side = "BUY" if signal == "LONG" else "SELL"
            broker_msg = self.broker.place_order("SPY", side, qty)

        msg = f"Entered {signal} on SPY at ~{price:.2f} with qty {qty}"
        if broker_msg:
            msg += f" | Broker: {broker_msg}"

        self._log(msg)

    def exit_trade(self, price):
        """Simulate exiting a trade and (optionally) sending to broker."""
        if self.position is None:
            return

        qty = self._estimate_quantity(price)

        broker_msg = None
        if self.broker is not None:
            side = "SELL" if self.position == "LONG" else "BUY"
            broker_msg = self.broker.close_position("SPY")

        msg = f"Exited {self.position} on SPY at ~{price:.2f} with qty {qty}"
        if broker_msg:
            msg += f" | Broker: {broker_msg}"

        self._log(msg)
        self.position = None

    def get_status(self):
        """Return bot status for UI display."""
        return {
            "position": self.position,
            "last_trade": self.last_trade,
            "log": self.log[-10:],  # last 10 entries
        }
