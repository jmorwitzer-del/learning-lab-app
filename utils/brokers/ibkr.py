class IBKRBroker:
    """
    Placeholder IBKR broker connector.
    Real API calls will be added in Stage 5.
    """

    def __init__(self):
        self.connected = False

    def connect(self):
        """Simulate connecting to IBKR."""
        self.connected = True
        return "Connected to IBKR (simulation mode)"

    def place_order(self, symbol, side, quantity):
        """Simulate placing an order."""
        return f"Simulated IBKR order: {side} {quantity} {symbol}"

    def close_position(self, symbol):
        """Simulate closing a position."""
        return f"Simulated IBKR close position: {symbol}"
