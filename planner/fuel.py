"""Step 4: choose where to buy fuel, and how much, so the trip costs as little as possible.

Fuel is counted in miles of driving. At each station, look one full tank ahead:
  1. A cheaper station is in reach?  Buy just enough to get to the first one.
  2. Nothing cheaper in reach?       Fill the tank, and go to the cheapest one in reach.
"""
TANK_MILES = 500  # maximum range
MPG = 10


class NoStationInReach(Exception):
    pass


def plan_fuel_stops(stations, total_miles, tank_miles=TANK_MILES, mpg=MPG):
    """stations: dicts with "mile" and "price". The truck starts with a full tank."""
    start = {"mile": 0, "price": float("inf")}  # nothing to buy at the start
    finish = {"mile": total_miles, "price": 0}  # "cheapest of all", so we never buy more than needed
    points = [start] + sorted(stations, key=lambda s: s["mile"]) + [finish]

    fuel = tank_miles
    here = 0
    purchases = []
    while points[here] is not finish:
        current = points[here]
        in_reach = [i for i in range(here + 1, len(points))
                    if points[i]["mile"] - current["mile"] <= tank_miles + 1e-9]
        if not in_reach:
            raise NoStationInReach(f"No fuel station within {tank_miles} miles after mile {current['mile']:.0f}.")

        cheaper = [i for i in in_reach if points[i]["price"] < current["price"]]
        if cheaper:  # rule 1
            target = cheaper[0]
            buy = max(0, points[target]["mile"] - current["mile"] - fuel)
        else:  # rule 2
            target = min(in_reach, key=lambda i: points[i]["price"])
            buy = tank_miles - fuel

        if buy > 1e-9:
            gallons = buy / mpg
            purchases.append({**current, "gallons": gallons, "cost": gallons * current["price"]})
        fuel += buy - (points[target]["mile"] - current["mile"])
        here = target
    return purchases
