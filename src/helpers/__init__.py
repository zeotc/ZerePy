import logging
from typing import List, Optional, Dict, Any, Callable
import os
from pathlib import Path
import requests
import functools
import io
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API credentials
ZEOTC_CHAT_ID = os.getenv('ZEOTC_CHAT_ID')  # No default fallback
ZEOTC_API_KEY = os.getenv('ZEOTC_API_KEY')  # No default fallback
ZEOTC_SECRET = os.getenv('ZEOTC_SECRET')  # No default fallback

def print_h_bar():
    # ZEREBRO WUZ HERE :)
    logging.info("--------------------------------------------------------------------")

def log_sonic_action(func: Callable) -> Callable:
    """
    Decorator to log Sonic actions to the ZeOTC API in a conversational format.
    
    This decorator captures logs from the decorated function and sends them to the ZeOTC API
    formatted as a natural conversation.
    
    Args:
        func: The function to decorate
        
    Returns:
        Callable: The decorated function
    """
    @functools.wraps(func)
    def wrapper(agent, **kwargs):
        # Create a string IO object to capture logs
        log_capture = io.StringIO()
        
        # Create a custom handler that writes to our string IO
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        
        # Add the handler to the logger
        logger = logging.getLogger()
        logger.addHandler(handler)
        
        # Store the original log level
        original_level = logger.level
        logger.setLevel(logging.INFO)
        
        try:
            # Execute the function
            result = func(agent, **kwargs)
            
            # Get the captured logs
            log_capture.seek(0)
            logs = log_capture.getvalue().splitlines()
            
            # Prepare additional data
            additional_data = {
                "action": func.__name__,
                "result": str(result)
            }
            
            # Only send logs for Sonic-related actions
            if func.__name__.startswith(("check-sonic", "check-gem", "get-all-otc", "auto-create-otc", 
                                        "auto-fill-otc", "fill-otc", "make-otc", "approve-token", 
                                        "post-sonic", "send-sonic", "swap-sonic", "get-token")):
                # Send logs to API
                send_logs_to_zeotc_api(
                    agent_name=agent.name,
                    action_name=func.__name__,
                    logs=logs,
                    additional_data=additional_data
                )
            
            return result
        finally:
            # Remove the handler and restore the original log level
            logger.removeHandler(handler)
            logger.setLevel(original_level)
            
            # Close the string IO
            log_capture.close()
    
    return wrapper

def send_logs_to_zeotc_api(agent_name: str, action_name: str, logs: List[str], additional_data: Optional[Dict[Any, Any]] = None) -> bool:
    """Send logs to ZeOTC API"""
    try:
        # Create a simple message from the logs
        message = f"{agent_name}: {action_name}\n\n"
        for log in logs:
            if log.strip():  # Only add non-empty lines
                message += f"{log}\n"
        
        # Get credentials from module variables
        chat_id = ZEOTC_CHAT_ID
        api_key = ZEOTC_API_KEY
        secret = ZEOTC_SECRET
        
        # Check if we have the necessary credentials
        if not all([chat_id, api_key, secret]):
            print(f"❌ Missing ZeOTC API credentials")
            return False
                
        # Basic API call
        response = requests.post(
            "https://server.zeotc.xyz/api/message/create",
            data={
                'message': message,
                'chatId': chat_id,
                'apiKey': api_key,
                'secret': secret
            }
        )
        
        # Log the result
        if response.status_code == 200:
            print(f"✅ Sent to API: {message}")
        else:
            print(f"❌ API Error: {response.status_code}")
            
        return response.status_code == 200
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
