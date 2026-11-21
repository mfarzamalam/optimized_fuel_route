"""The API: GET /api/route/?start=New York, NY&finish=Los Angeles, CA"""
from django.http import JsonResponse

from .fuel import NoStationInReach, plan_fuel_stops
from .places import PlaceNotFound, find_city
from .routing import RoutingError, get_route
from .stations import stations_near_route


def route_view(request):
    start, finish = request.GET.get("start"), request.GET.get("finish")
    if not start or not finish:
        return JsonResponse({"error": 'Send both "start" and "finish", e.g. ?start=Dallas, TX&finish=Denver, CO'}, status=400)

    try:
        route = get_route(find_city(start), find_city(finish))  # steps 1 + 2
        stations = stations_near_route(route)                   # step 3
        purchases = plan_fuel_stops(stations, route.miles)      # step 4
    except PlaceNotFound as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    except NoStationInReach as exc:
        return JsonResponse({"error": str(exc)}, status=422)
    except RoutingError as exc:
        return JsonResponse({"error": str(exc)}, status=502)

    return JsonResponse({
        "start": start,
        "finish": finish,
        "distance_miles": round(route.miles, 1),
        "number_of_stops": len(purchases),
        "fuel_stops": [
            {
                "name": p["name"], "address": p["address"], "city": p["city"], "state": p["state"],
                "mile": round(p["mile"], 1),
                "price_per_gallon": round(p["price"], 3),
                "gallons": round(p["gallons"], 2),
                "cost": round(p["cost"], 2),
            }
            for p in purchases
        ],
        "total_gallons": round(sum(p["gallons"] for p in purchases), 2),
        "total_fuel_cost": round(sum(p["cost"] for p in purchases), 2),
    })
