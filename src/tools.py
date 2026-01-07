import json
from src.database import get_medication_by_name, get_user_by_id, get_active_prescriptions, get_medication_by_id


# --- 1. The Actual Python Functions ---

def get_medication_details(medication_name: str):
    """
    Gets details about a medication including active ingredients, dosage, and if it requires a prescription.
    
    Args:
        medication_name (str): The name of the medication to look up.
        
    Returns:
        (str): a JSON string with medication details.
        
    Error handling:
        Returns a JSON string of an error message if medication not found.
        
    Fallback behavior:
        Agent should ask to clarify the medication name or tell the user it doesn't exist in inventory.
        Agent should ask to clarify the medication name or tell the user it doesn't exist (depending on the context).
    """        
    med = get_medication_by_name(medication_name)
    if med:
        return json.dumps(med) # Return as string for the LLM
    return json.dumps({"error": "Medication not found."})

def check_inventory(medication_name: str):
    """
    Checks the current stock level of a medication.
    
    Args:
        medication_name (str): The name of the medication to look up.
        
    Returns:
        (str): a JSON string with medication quantity in stock.
        
    Error handling:
        Returns a JSON string of an error message if medication not found.
        
    Fallback behavior:
        Agent should ask to clarify the medication name or tell the user it doesn't exist in inventory.
    """
    # We need to find the med by ID from the DB
    # (In a real app, this would be a direct DB query. Here we scan the file)
    medicine = get_medication_by_name(medication_name)
    if medicine:
            return json.dumps({"stock": medicine["stock_quantity"]})
    return json.dumps({"error": "Medication ID not found."})

def validate_prescription(user_id: str, medication_name: str):
    """
    Checks if a user has a valid prescription for a specific medication.
    
    Args:
        user_id (str): The ID of the user whose prescription is being looked up.
        medication_name (str): The name of the medication to look up.

    Returns:
        (str): a JSON string with The user name and True if they have a prescription or False if not.
        
    Error handling:
        Returns a JSON string of an error message if user not found or medication was not found.
        
    Fallback behavior:
        If medication not found Agent asks the user to clarify the medication name or tell them it doesn't exist in the inventory.
        If user not found, agent should inform the user that their ID is invalid and asks them to verify their identity.
        (Note in this version of the project users can't login or sign up yet)
    """
    user = get_user_by_id(user_id)
    if not user:
        return json.dumps({"error": "User not found."})
    
    medication = get_medication_by_name(medication_name)
    if not medication:
        return json.dumps({"error": "Medication not found."})

    medication_id = medication["id"]
    # Checks if the user has the medication_id in their active_prescriptions list
    has_prescription = medication_id in user["active_prescriptions"]
    
    return json.dumps({
        "user": user["name"],
        "has_valid_prescription": has_prescription
    })

def list_user_prescriptions(user_id: str):
    """
    Gets a list of all active prescriptions for a specific user.
    
    Args:
        user_id (str): The ID of the user whose prescriptions are being looked up.
        
    Returns:
        (str): a JSON string that lists all active prescriptions for the user.
        (can be an empty list if doesn't have active prescriptions)
        
    Error handling:
        Returns a JSON string of an error message if user not found.
        
    Fallback behavior:
        If user not found, agent should inform the user that their ID is invalid and asks them to verify their identity.
        (Note in this version of the project users can't login or sign up yet).
    """
    user = get_user_by_id(user_id)
    if not user:
        return json.dumps({"error": "User not found."})

    result = get_active_prescriptions(user_id)
    if result is None:
        # Redundant check, but for safety in case implementation changes
        return json.dumps({"error": "User not found."})
    
    return json.dumps(result)


# --- 2. The "Menu" (Schemas) for OpenAI ---
# This is what tells the AI how to use the tools above.

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "get_medication_details",
            "description": "Gets details about a medication including active ingredients, dosage, and if it requires a prescription. Use this when a user asks about a drug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication (e.g., 'Acamol', 'Nurofen')."
                    }
                },
                "required": ["medication_name"],
                "additionalProperties": False, # Make sure the Agent passes exactly the required parameters the way they are defined
            },
        "strict": True, # Make sure the Agent passes exactly the required parameters the way they are defined
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Checks the current stock level of a medication. You MUST provide the medication_id, not the name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication (e.g., 'Acamol', 'Nurofen')."
                    }
                },
                "required": ["medication_name"],
                "additionalProperties": False,
            },
        "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "validate_prescription",
            "description": "Checks if a user has a valid prescription for a specific medication, use it when a user asks if they have a prescription for some medicine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID (e.g., 'user_101')."
                    },
                    "medication_name": {
                        "type": "string",
                        "description": "The name of the medication to check."
                    }
                },
                "required": ["user_id", "medication_name"],
                "additionalProperties": False,
            },
        "strict": True,
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_prescriptions",
            "description": "Gets a list of all active prescriptions for a specific user. Use this when a user asks 'What prescriptions do I have?'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user's ID (e.g., 'user_101')."
                    }
                },
                "required": ["user_id"],
                "additionalProperties": False,
            },
        "strict": True,
        }
    }    
]

# A dictionary to help our code map the string name to the actual function
available_functions = {
    "get_medication_details": get_medication_details,
    "check_inventory": check_inventory,
    "validate_prescription": validate_prescription,
    "list_user_prescriptions": list_user_prescriptions
}