
import datetime
from utils.alpha_live import live_divergence_signal


class BotEngine:
    """
    Core trading bot engine (simulation mode).
    Handles:
      - Live signal intake
      - Market-open entry logic
      - Market-close exit logic
      - Logging
      - Broker abstraction (placeholder)
    """

    def __init__(self):
            def set_broker(self, broker_name):
        """Assign a broker connector (simulation mode)."""
        if broker_name == "Interactive Brokers (IBKR)":
            from utils.brokers.ibkr import IBKRBroker
            self.broker = IBKRBroker()
        elif broker_name == "Alpaca":
            from utils.brokers.alpaca import AlpacaBroker
            self.broker = AlpacaBroker()
        else:
            self.broker = None

        self.position = None        # "LONG", "SHORT", or None
        self.last_trade = None      # record of last executed trade
        self.log = []               # list of trade logs

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

    def enter_trade(self, signal):
        """Simulate entering a trade."""
        self.position = signal
        timestamp = datetime.datetime.now()
        self.last_trade = f"Entered {signal} at {timestamp}"
        self.log.append(self.last_trade)

    def exit_trade(self):
        """Simulate exiting a trade."""
        timestamp = datetime.datetime.now()
        exit_msg = f"Exited {self.position} at {timestamp}"
        self.log.append(exit_msg)
        self.last_trade = exit_msg
        self.position = None

    def get_status(self):
        """Return bot status for UI display."""
        return {
            "position": self.position,
            "last_trade": self.last_trade,
            "log": self.log[-10:],  # last 10 entries
        }
    def execute_order(self, side, symbol="SPY", quantity=1):
        """Simulate sending an order to the selected broker."""
        if self.broker is None:
            return "No broker selected."

        if not self.broker.connected:
            self.broker.connect()

        return self.broker.place_order(symbol, side, quantity)
