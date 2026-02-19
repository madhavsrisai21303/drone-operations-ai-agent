from assignment import find_best_pilot, find_best_drone
from conflict import (
    check_budget,
    location_mismatch,
    check_pilot_conflict
)
from utils import update_pilots, update_missions


def handle_message(message, pilots, drones, missions):
    message = message.lower()
    response = "I'm sorry, I didn't understand that. Try commands like 'assign mission 123', 'show available pilots', 'show maintenance drones', or 'update pilot John to Available'."

    # ASSIGN MISSION
    if "assign" in message and "mission" in message:
        words = message.split()
        mission_id = None
        for word in words:
            if word.isdigit():
                mission_id = int(word)
                break
        if mission_id:
            response = assign_mission(mission_id, pilots, drones, missions)
        else:
            response = "Please specify a valid mission ID (e.g., 'assign mission 123')."

    # SHOW AVAILABLE PILOTS
    elif "available pilots" in message:
        available_pilots = pilots[pilots["status"] == "Available"]
        if not available_pilots.empty:
            response = "Available Pilots:\n" + "\n".join(
                [f"- {row['name']} (Skills: {row['skills']}, Location: {row['location']})" for _, row in available_pilots.iterrows()])
        else:
            response = "No available pilots at the moment."

    # SHOW MAINTENANCE DRONES
    elif "maintenance" in message:
        maintenance_drones = drones[drones["status"] == "Maintenance"]
        if not maintenance_drones.empty:
            response = "Drones in Maintenance:\n" + "\n".join(
                [f"- {row['drone_id']} (Location: {row['location']})" for _, row in maintenance_drones.iterrows()])
        else:
            response = "No drones in maintenance."

    # UPDATE PILOT STATUS
    elif "update" in message and "to" in message:
        words = message.split()
        pilot_name = None
        new_status = None
        try:
            pilot_name = words[words.index("pilot") + 1]
            new_status = words[words.index("to") + 1]
        except (ValueError, IndexError):
            pass
        if pilot_name and new_status:
            if pilot_name in pilots["name"].values:
                pilots.loc[pilots["name"] == pilot_name, "status"] = new_status.capitalize()
                update_pilots(pilots)
                response = f"Pilot {pilot_name} status updated to {new_status.capitalize()}."
            else:
                response = f"Pilot {pilot_name} not found."
        else:
            response = "Please specify pilot name and status (e.g., 'update pilot John to Available')."

    return response, pilots, drones, missions


def assign_mission(mission_id, pilots, drones, missions):
    mission_rows = missions[missions["project_id"] == mission_id]

    if mission_rows.empty:
        return f"Mission {mission_id} not found."

    mission = mission_rows.iloc[0]

    pilot = find_best_pilot(pilots, mission, missions)
    drone = find_best_drone(drones, mission)

    if pilot is None:
        return "No suitable pilot available for this mission."

    if drone is None:
        return "No suitable drone available for this mission."

    # Conflict checks
    if check_pilot_conflict(pilot, mission, missions):
        return f"Pilot {pilot['name']} has a scheduling conflict."

    budget_warning, cost = check_budget(pilot, mission)

    warnings = []

    if budget_warning:
        warnings.append(f"Budget exceeded: Estimated cost ${cost}, Budget ${mission['budget']}")

    if location_mismatch(pilot, drone, mission):
        warnings.append("Location mismatch between pilot, drone, and mission.")

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
    Estimated Cost: ${cost}
    """

    if warnings:
        response += "\nWarnings:\n" + "\n".join(warnings)

    return response
