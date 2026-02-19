from assignment import find_best_pilot, find_best_drone
from conflict import (
    check_budget,
    location_mismatch,
    check_pilot_conflict
)
from utils import update_pilots, update_missions


def handle_message(message, pilots, drones, missions):
    message = message.lower()

    # ASSIGN MISSION
    if "assign" in message and "mission" in message:
        words = message.split()
        mission_id = None

        for word in words:
            if word.upper().startswith("M"):
                mission_id = word.upper()

        if mission_id:
            return assign_mission(mission_id, pilots, drones, missions)
        else:
            return "Please specify mission ID (e.g., M1).", pilots, drones, missions

    # SHOW AVAILABLE PILOTS
    if "available pilots" in message:
        available = pilots[pilots["status"] == "Available"]
        if available.empty:
            return "No available pilots found.", pilots, drones, missions
        return available.to_string(index=False), pilots, drones, missions

    # SHOW MAINTENANCE DRONES
    if "maintenance" in message:
        maint = drones[drones["status"] == "Maintenance"]
        if maint.empty:
            return "No drones currently in maintenance.", pilots, drones, missions
        return maint.to_string(index=False), pilots, drones, missions

    # UPDATE PILOT STATUS
    if "update" in message and "to" in message:
        words = message.split()
        try:
            name = words[1].capitalize()
            status = words[-1].capitalize()

            if name not in pilots["name"].values:
                return f"Pilot {name} not found.", pilots, drones, missions

            pilots.loc[pilots["name"] == name, "status"] = status
            update_pilots(pilots)

            return f"Updated {name} to {status}.", pilots, drones, missions

        except:
            return "Invalid update format. Example: Update Alice to On Leave", pilots, drones, missions

    return "Command not recognized.", pilots, drones, missions


def assign_mission(mission_id, pilots, drones, missions):

    mission_rows = missions[missions["project_id"] == mission_id]

    if mission_rows.empty:
        return "Mission not found.", pilots, drones, missions

    mission = mission_rows.iloc[0]

    pilot = find_best_pilot(pilots, mission, missions)
    drone = find_best_drone(drones, mission)

    if pilot is None:
        return "No suitable pilot found.", pilots, drones, missions

    if drone is None:
        return "No suitable drone found.", pilots, drones, missions

    # Conflict checks
    if check_pilot_conflict(pilot, mission, missions):
        return "Pilot has scheduling conflict.", pilots, drones, missions

    budget_warning, cost = check_budget(pilot, mission)

    warnings = []

    if budget_warning:
        warnings.append("⚠ Budget exceeded.")

    if location_mismatch(pilot, drone, mission):
        warnings.append("⚠ Location mismatch detected.")

    # Update mission
    missions.loc[missions["project_id"] == mission_id, "assigned_pilot"] = pilot["name"]
    missions.loc[missions["project_id"] == mission_id, "assigned_drone"] = drone["drone_id"]

    # Update pilot status
    pilots.loc[pilots["name"] == pilot["name"], "status"] = "Assigned"

    # Write back to Google Sheets
    update_pilots(pilots)
    update_missions(missions)

    response = f"""
    ✅ Mission Assigned Successfully

    Pilot: {pilot['name']}
    Drone: {drone['drone_id']}
    Estimated Cost: {cost}
    """

    if warnings:
        response += "\n\nWarnings:\n" + "\n".join(warnings)

    return response, pilots, drones, missions
