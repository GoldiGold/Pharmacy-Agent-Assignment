import json
import os
from CONSTS import DATABASE_PATH

def load_data():
    """
    loads the pharmacy data from the JSON file.
    assuming the file located in DATABASE_PATH is valid and accessible.
    
    Returns:
        (dict): The loaded data from the JSON file.
    """    
    with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
    
def get_medication_by_name(medication_name: str, data=None):
    """
    Returns a dictionary with the medication details for a given medication name.

    Args:
        medication_name (str): Then name of the medication to look up
        data (dict, optional): The loaded data from the JSON file. Defaults to None.

    Returns:
        med (dict): The medication details if found, otherwise None.
    """
    data = data or load_data()
    # Case-insensitive search
    for med in data["medications"]:
        if med["name"].lower() == medication_name.lower():
            return med
    return None

def get_medication_by_id(medication_id: str, data=None):
    """
    Returns a dictionary with the medication details for a given medication id.

    Args:
        medication_id (str): The ID of the medication to look up.
        data (dict, optional): The loaded data from the JSON file. Defaults to None.
    
    Returns:
        med (dict): The medication details if found, otherwise None.
    """
    data = data or load_data()
    for med in data["medications"]:
        if med["id"] == medication_id:
            return med
    return None

def get_user_by_id(user_id: str, data=None):
    """
    Returns a dictionary with the user details for a given user id.

    Args:
        user_id (str): The ID of the user to look up.
        data (dict, optional): The loaded data from the JSON file. Defaults to None.
    
    Returns:
        user (dict): The user details if found, otherwise None.
    """
    data = data or load_data()
    for user in data["users"]:
        if user["id"] == user_id:
            return user
    return None

def get_active_prescriptions(user_id: str, data=None):
    """
    Returns a list of medication details for a user's active prescriptions.

    Args:
        user_id (str): The ID of the user to look up.
        data (dict, optional): The loaded data from the JSON file. Defaults to None.

    Returns:
        list: A list of medication details for a user's active prescriptions.
    """
    data = data or load_data()
    
    # 1. Find the user
    user = get_user_by_id(user_id, data=data)
            
    if not user:
        return None  # User not found
        
    # 2. Add Medications to list
    prescription_details = []
    for med_id in user["active_prescriptions"]:
        # Find the matching medication object
        medicine = get_medication_by_id(med_id, data=data)
        if medicine:
            prescription_details.append({
                "medication": medicine["name"],
                "id": medicine["id"],
                # "dosage": medicine["dosage_instructions"] #TODO: DECIDE IF WE WANT TO ADD DOSAGE INFO HERE
            })
                
    return {
        "user_name": user["name"],
        "active_prescriptions": prescription_details
    }
