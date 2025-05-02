import logging
from typing import Dict, Any
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.trading_behavior")

class TradingBehaviorConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        logger.info("Initializing Trading Behavior connection...")
        super().__init__(config)
        
        # Extract trading parameters from config
        self.fill_threshold = config.get("fill_threshold", 2.0)
        self.random_fill_chance = config.get("random_fill_chance", 0.2)
        self.randomness_min = config.get("randomness_min", 0.5)
        self.randomness_max = config.get("randomness_max", 1.5)
        
        logger.info(f"Trading behavior initialized with fill threshold: {self.fill_threshold}")

    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Trading Behavior configuration from JSON"""
        # All fields are optional with defaults
        return config

    def register_actions(self) -> None:
        """Register actions for the Trading Behavior connection"""
        self.actions = {
            "get-parameters": Action(
                name="get-parameters",
                parameters=[],
                description="Get trading behavior parameters"
            ),
            "get-fill-threshold": Action(
                name="get-fill-threshold",
                parameters=[],
                description="Get fill threshold for OTC asks"
            ),
            "get-random-chance": Action(
                name="get-random-chance",
                parameters=[],
                description="Get random fill chance"
            )
        }

    def get_parameters(self) -> Dict[str, Any]:
        """Get all trading behavior parameters"""
        return {
            "fill_threshold": self.fill_threshold,
            "random_fill_chance": self.random_fill_chance,
            "randomness_min": self.randomness_min,
            "randomness_max": self.randomness_max
        }
        
    def get_fill_threshold(self) -> float:
        """Get fill threshold for OTC asks"""
        return self.fill_threshold
        
    def get_random_chance(self) -> float:
        """Get random fill chance"""
        return self.random_fill_chance

    def configure(self) -> bool:
        """No interactive configuration needed for trading behavior"""
        return True

    def is_configured(self, verbose: bool = False) -> bool:
        """Trading behavior is always configured"""
        return True
        
    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Trading Behavior action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")
            
        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs) 