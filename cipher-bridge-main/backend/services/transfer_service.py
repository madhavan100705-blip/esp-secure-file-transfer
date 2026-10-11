from backend.esp.simulator import TransferSimulator

simulator = TransferSimulator()

def run_transfer(filename: str, data: bytes, attack: bool = False) -> dict:
    return simulator.transfer(filename, data, attack)

def reset() -> dict:
    global simulator
    simulator = TransferSimulator()
    return simulator.stats.copy()

def status() -> dict:
    return {"mode": "python_backend", "stats": simulator.stats.copy(), "sequence": simulator.sequence}
