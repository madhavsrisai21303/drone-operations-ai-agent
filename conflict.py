from datetime import datetime


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def check_date_overlap(start1, end1, start2, end2):
    return parse_date(start1) <= parse_date(end2) and parse_date(start2) <= parse_date(end1)


def check_pilot_conflict(pilot, mission, missions):
    for _, m in missions.iterrows():
        if m["assigned_pilot"] == pilot["name"]:
            if check_date_overlap(
                m["start_date"], m["end_date"],
                mission["start_date"], mission["end_date"]
            ):
                return True
    return False


def check_budget(pilot, mission):
    start = parse_date(mission["start_date"])
    end = parse_date(mission["end_date"])
    duration = (end - start).days + 1
    total_cost = duration * pilot["daily_rate"]
    return total_cost > mission["budget"], total_cost


def check_weather(drone, mission):
    if mission.get("weather", "").lower() == "rainy" and drone.get("weather_rating", "") != "IP43":
        return True
    return False


def check_maintenance(drone):
    return drone.get("status", "") == "Maintenance"


def location_mismatch(pilot, drone, mission):
    if pilot["location"] != mission["location"]:
        return True
    if drone["location"] != mission["location"]:
        return True
    return False
