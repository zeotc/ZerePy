import logging
import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.zeotc_connection")

class ZeOTCConnectionError(Exception):
    """Base exception for ZeOTC connection errors"""
    pass

class ZeOTCConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing ZeOTC connection...")
        # Load environment variables first
        load_dotenv()
        
        # Make a copy of the config to avoid modifying the original
        config_copy = config.copy() if config else {}
        
        # Get API URL, key and chat_id from environment
        self.base_url = os.getenv('ZEOTC_API_URL', 'https://server.zeotc.xyz/api')
        self.api_key = os.getenv('ZEOTC_API_KEY')
        self.chat_id = os.getenv('ZEOTC_CHAT_ID')
        
        # Initialize base class with the config copy
        super().__init__(config_copy)
        
        # Log initialization but don't expose sensitive data in logs
        if self.api_key:
            logger.info("ZeOTC API key found in environment")
        else:
            logger.info("ZeOTC API key not found in environment - some features may not work")

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate ZeOTC configuration from JSON"""
        return config

    def register_actions(self) -> None:
        self.actions = {
            "send-message": Action(
                name="send-message",
                parameters=[
                    ActionParameter("message", True, str, "Message to send")
                ],
                description="Send a message to the ZeOTC chat"
            ),
            "get-messages": Action(
                name="get-messages",
                parameters=[],
                description="Get recent messages from the ZeOTC chat"
            )
        }

    def configure(self) -> bool:
        logger.info("\n🔷 ZEOTC SETUP")
        if self.is_configured():
            logger.info("ZeOTC connection is already configured")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return True

        try:
            if not os.path.exists('.env'):
                with open('.env', 'w') as f:
                    f.write('')

            # Get API URL
            api_url = input("\nEnter ZeOTC API URL (or press Enter for default): ").strip()
            if api_url:
                os.environ['ZEOTC_API_URL'] = api_url
                with open('.env', 'a') as f:
                    f.write(f"\nZEOTC_API_URL={api_url}")
            else:
                # Set default if not provided
                api_url = "https://server.zeotc.xyz/api"
                os.environ['ZEOTC_API_URL'] = api_url
                with open('.env', 'a') as f:
                    f.write(f"\nZEOTC_API_URL={api_url}")

            # Get API Key
            api_key = input("\nEnter ZeOTC API Key: ").strip()
            if api_key:
                os.environ['ZEOTC_API_KEY'] = api_key
                with open('.env', 'a') as f:
                    f.write(f"\nZEOTC_API_KEY={api_key}")
                    
            # Get Chat ID (optional)
            chat_id = input("\nEnter ZeOTC Chat ID (optional): ").strip()
            if chat_id:
                os.environ['ZEOTC_CHAT_ID'] = chat_id
                with open('.env', 'a') as f:
                    f.write(f"\nZEOTC_CHAT_ID={chat_id}")

            logger.info("\n✅ ZeOTC connection configured successfully")
            return True

        except Exception as e:
            logger.error(f"Configuration failed: {e}")
            return False

    def is_configured(self, verbose: bool = False) -> bool:
        try:
            load_dotenv()
            missing_vars = []
            
            # Check for API key - only this is required
            if not os.getenv('ZEOTC_API_KEY'):
                missing_vars.append("ZEOTC_API_KEY")
                
            if missing_vars and verbose:
                logger.warning(f"Missing ZeOTC configuration: {', '.join(missing_vars)}")
                
            # Only require the API key for basic configuration
            return 'ZEOTC_API_KEY' not in missing_vars
                
        except Exception as e:
            if verbose:
                logger.error(f"Configuration check failed: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """Send a message to the ZeOTC chat"""
        try:
            url = f"{self.base_url}/message/create"
            
            if not self.chat_id:
                logger.error("No ZEOTC_CHAT_ID specified in environment")
                return False
            
            # Prepare the request data
            data = {
                "message": message,
                "chatId": self.chat_id
            }
            
            # Prepare headers with API key
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            else:
                logger.error("Missing API key for message sending")
                return False
            
            # Send the message
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()
            logger.info(f"Message sent successfully to chat {self.chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get recent messages from the ZeOTC chat"""
        try:
            if not self.chat_id:
                logger.error("No ZEOTC_CHAT_ID specified in environment")
                return []
                
            url = f"{self.base_url}/message/list?chatId={self.chat_id}"
            
            # Prepare headers with API key
            headers = {}
            if self.api_key:
                headers["x-api-key"] = self.api_key
            else:
                logger.error("Missing API key for fetching messages")
                return []
                
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if the response has the expected structure
            if not isinstance(data, dict):
                logger.error(f"Unexpected response format: {data}")
                return []
                
            # Check for error status in the response
            if data.get("status") == "error":
                logger.error(f"API returned error: {data.get('message', 'Unknown error')}")
                return []
                
            # The API response structure might include messages in a result field
            # If not present or empty, check if messages might be in a different field
            messages = data.get("result", [])
            
            # Handle other possible response structures
            if not messages and "messages" in data:
                messages = data.get("messages", [])
                
            # Ensure we have a list of dictionaries
            if not isinstance(messages, list):
                logger.error(f"Unexpected messages format: {messages}")
                return []
                
            # Log the number of messages retrieved
            logger.info(f"Retrieved {len(messages)} messages from chat {self.chat_id}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a ZeOTC action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")
            
        # Check if we have an API key - it's required for all actions
        if not self.api_key:
            logger.error("Cannot perform ZeOTC action: Missing API key")
            if action_name == "get-messages":
                return []
            return False
        
        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs) 