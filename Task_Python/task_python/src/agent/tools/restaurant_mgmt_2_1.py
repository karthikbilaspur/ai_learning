
import structlog
from typing import List, Dict

logger = structlog.get_logger()

# Original tkinter logic preserved as backend logic
MENU_PRICES = {
    "fries": 2.5,
    "burger": 5.0,
    "filet": 7.5,
    "chicken_burger": 6.0,
    "cheese_burger": 6.5,
    "drinks": 2.0
}

class RestaurantBackend:
    def calculate_total(self, order: Dict[str, float]):
        try:
            total_cost = sum(float(order.get(k,0))*v for k,v in MENU_PRICES.items() if k in order)
            # original calculation also allowed direct amounts, support both
            # if values are already amounts (from original tkinter), just sum
            if total_cost == 0:
                total_cost = sum(float(v) for v in order.values())
            service_charge = total_cost * 0.1
            tax = total_cost * 0.08
            sub_total = total_cost + service_charge + tax
            return {
                "cost": round(total_cost,2),
                "service_charge": round(service_charge,2),
                "tax": round(tax,2),
                "sub_total": round(sub_total,2),
                "total": round(sub_total,2)
            }
        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")

backend = RestaurantBackend()

# Original Tkinter class kept for local GUI run (not used in API)
try:
    from tkinter import *
    class RestaurantManagementSystem:
        def __init__(self, root):
            self.root = root
            self.root.title("Restaurant Management System")
            # ... original GUI code kept ...
            pass
except ImportError:
    RestaurantManagementSystem = None

def run(params: dict):
    logger.info("tool_start", tool="restaurant", params=params)
    action = params.get("action", "menu")
    if action == "menu":
        return {"menu": MENU_PRICES, "note": "Prices per item"}
    if action == "order":
        order = params.get("items", params.get("order", {}))
        # allow list ["fries","burger"] or dict {"fries":2}
        if isinstance(order, list):
            order_dict = {k:1 for k in order}
        else:
            order_dict = order
        total = backend.calculate_total(order_dict)
        return {"order": order_dict, **total, "status": "order calculated"}
    if action == "reset":
        return {"status": "reset - clear order"}
    raise ValueError("action must be menu|order|reset")
