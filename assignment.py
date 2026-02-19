from conflict import check_maintenance, check_weather


def score_pilot(pilot, mission):
    score = 0

    # Skill match
    if mission["required_skill"] in pilot["skills"]:
        score += 5

    # Location match
    if pilot["location"] == mission["location"]:
        score += 3

    # Availability
    if pilot["status"] == "Available":
        score += 5

    return score


def find_best_pilot(pilots, mission, missions):
    candidates = []

    for _, pilot in pilots.iterrows():

        # Must have required skill
        if mission["required_skill"] not in pilot["skills"]:
            continue

        # Must be available
        if pilot["status"] != "Available":
            continue

        score = score_pilot(pilot, mission)
        candidates.append((score, pilot))

    if not candidates:
        return None

    candidates.sort(reverse=True, key=lambda x: x[0])
    return candidates[0][1]


def find_best_drone(drones, mission):
    candidates = []

    for _, drone in drones.iterrows():

        # Must be available
        if drone["status"] != "Available":
            continue

        # Cannot be in maintenance
        if check_maintenance(drone):
            continue
