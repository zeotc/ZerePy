import logging
import random
from typing import Dict, Any, List
from src.action_handler import register_action
from src.helpers import print_h_bar
import time
from src.prompts import ZEOTC_REPLY_PROMPT, ZEOTC_DISCUSSION_PROMPT
import os

logger = logging.getLogger("actions.zeotc_actions")

# Define token addresses and rarity factors
GEM_TOKENS = {
    "coral": "0x1234567890abcdef1234567890abcdef12345678",
    "diamond": "0x2345678901abcdef2345678901abcdef23456789",
    "flurite": "0x3456789012abcdef3456789012abcdef34567890",
    "malachite": "0x4567890123abcdef4567890123abcdef45678901",
    "obsidian": "0x5678901234abcdef5678901234abcdef56789012",
    "onyx": "0x6789012345abcdef6789012345abcdef67890123",
    "opal": "0x7890123456abcdef7890123456abcdef78901234",
    "quartz": "0x8901234567abcdef8901234567abcdef89012345",
    "ruby": "0x9012345678abcdef9012345678abcdef90123456",
    "topaz": "0x0123456789abcdef0123456789abcdef01234567"
}

# Define rarity factors for pricing
RARITY_FACTOR = {
    "coral": 1.0,
    "diamond": 4.0,
    "flurite": 1.5,
    "malachite": 2.0,
    "obsidian": 2.5,
    "onyx": 1.8,
    "opal": 3.0,
    "quartz": 1.2,
    "ruby": 3.5,
    "topaz": 2.2
}

@register_action("discuss-trading-opportunity")
def discuss_trading_opportunity(agent, **kwargs):
    """Discuss a trading opportunity with other agents in the ZeOTC chat.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n💬 DISCUSSING TRADING OPPORTUNITY")
        print_h_bar()
        
        # Check if ZeOTC connection is available
        if "zeotc" not in agent.connection_manager.connections:
            logger.error("ZeOTC connection not available")
            return False
            
        # Get recent OTC asks from agent state
        if "otc_asks" not in agent.state or not agent.state["otc_asks"]:
            logger.info("No OTC asks in state, fetching from contract...")
            from src.actions.sonic_actions import get_all_otc_asks
            get_all_otc_asks(agent)
            if not agent.state.get("otc_asks"):
                logger.info("No OTC asks available to discuss after fetch")
                return False
            
        asks = agent.state["otc_asks"]
        
        # Score and sort asks by attractiveness
        scored_asks = []
        
        for ask in asks:
            # Skip asks with missing fields
            required_fields = ["maker", "have_symbol", "want_symbol", "amount_have", "amount_want"]
            if not all(field in ask for field in required_fields):
                continue
                
            maker = ask["maker"]
            have_symbol = ask["have_symbol"]
            want_symbol = ask["want_symbol"]
            amount_have = ask["amount_have"]
            amount_want = ask["amount_want"]
            
            # Calculate a "fair price" and compare with the actual rate
            # This is a simplified model - in reality you'd use external price feeds
            
            # Get token addresses (if available in our mapping)
            have_token_name = have_symbol.lower()
            want_token_name = want_symbol.lower()
            
            # Get rarity factors, default to 1.0 if not found
            have_rarity = RARITY_FACTOR.get(have_token_name, 1.0)
            want_rarity = RARITY_FACTOR.get(want_token_name, 1.0)
            
            # Calculate relative value and price ratio
            # Lower ratio = better deal for buyer
            fair_price = have_rarity / want_rarity
            actual_price = amount_want / max(amount_have, 0.0001)  # Avoid division by zero
            
            price_ratio = actual_price / max(fair_price, 0.0001)  # Avoid division by zero
            
            # Calculate an overall "deal score" - lower is better
            # Add some randomness to simulate imperfect market information
            randomness = random.uniform(0.7, 1.3)
            deal_score = price_ratio * randomness
            
            # If this agent has a trading_behavior config, use it to adjust the score
            trading_config = next(
                (config for config in agent.config if config["name"] == "trading_behavior"), 
                None
            )
            
            if trading_config:
                # Increase chance of filling asks if price is favorable
                if price_ratio <= trading_config.get("fill_threshold", 3.0):
                    # This is a good deal, boost the score
                    deal_score *= 0.5
                
                # Add random chance for taking random trades
                random_fill = random.random() < trading_config.get("random_fill_chance", 0.2)
                if random_fill:
                    # Apply a random boost/penalty based on configured randomness
                    min_random = trading_config.get("randomness_min", 0.5)
                    max_random = trading_config.get("randomness_max", 1.5)
                    deal_score *= random.uniform(min_random, max_random)
            
            scored_asks.append({
                'maker': maker,
                'have_symbol': have_symbol.upper(),
                'want_symbol': want_symbol.upper(),
                'amount_have': amount_have,
                'amount_want': amount_want,
                'price_ratio': price_ratio,
                'fair_price': fair_price,
                'deal_score': deal_score
            })
            
        if not scored_asks:
            logger.info("No suitable asks found to discuss")
            return False
            
        # Sort by deal score (lower is better)
        scored_asks.sort(key=lambda x: x['deal_score'])
        
        # Select the best ask to discuss
        best_ask = scored_asks[0]
        
        # Generate a message using LLM about the trading opportunity
        agent_traits = getattr(agent, 'traits', ["normal"])
        if not isinstance(agent_traits, list):
            agent_traits = [agent_traits]
            
        # Get token balances to include in the prompt
        token_balances = "Unknown"
        if "gem_balances" in agent.state:
            token_balances = ", ".join([f"{name.upper()}: {balance}" for name, balance in agent.state.get("gem_balances", {}).items() if balance > 0])
            if not token_balances:
                token_balances = "No tokens currently held"
            
        # Create a prompt for the LLM to generate a message
        prompt = ZEOTC_DISCUSSION_PROMPT.format(
            amount_have=best_ask['amount_have'],
            have_symbol=best_ask['have_symbol'],
            amount_want=best_ask['amount_want'],
            want_symbol=best_ask['want_symbol'],
            price_ratio=best_ask['price_ratio'],
            agent_name=agent.name,
            agent_traits=", ".join(agent_traits),
            token_balances=token_balances
        )
        
        logger.info(f"Generating trading discussion for {best_ask['have_symbol']}/{best_ask['want_symbol']} trade...")
        
        # Use the LLM to generate the message
        system_prompt = agent._construct_system_prompt()
        message = agent.prompt_llm(prompt=prompt, system_prompt=system_prompt)
        
        if not message:
            logger.error("Failed to generate trading discussion from LLM")
            return False
            
        logger.info(f"Generated discussion: {message[:100]}...")
        
        # Send the message to the ZeOTC chat
        result = agent.connection_manager.perform_action(
            connection_name="zeotc",
            action_name="send-message",
            params={"message": message}
        )
        
        # Also tweet about this opportunity if it's a good deal
        if "twitter" in agent.connection_manager.connections and best_ask['deal_score'] < 1.5:
            # Only tweet about really good deals (deal_score < 1.5)
            try:
                # Generate a tweet prompt for this opportunity (could add a dedicated prompt here)
                tweet_text = f"Just spotted an amazing OTC trade: {best_ask['amount_have']} {best_ask['have_symbol']} for {best_ask['amount_want']} {best_ask['want_symbol']}! Rate: {best_ask['price_ratio']:.2f}x fair value! #OTCtrading #Crypto2060"
                
                # Post the tweet
                tweet_result = agent.connection_manager.perform_action(
                    connection_name="twitter",
                    action_name="post-tweet",
                    params={"message": tweet_text}
                )
                
                if tweet_result:
                    logger.info("✅ Successfully tweeted about trading opportunity")
                    # Update the last tweet time to prevent too frequent tweeting
                    agent.state["last_sonic_tweet_time"] = int(time.time())
            except Exception as e:
                logger.error(f"Error tweeting about trading opportunity: {e}")
        
        if result:
            logger.info("✅ Successfully discussed trading opportunity")
            return True
        else:
            logger.error("Failed to send message to ZeOTC chat")
            return False
            
    except Exception as e:
        logger.error(f"Error discussing trading opportunity: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

@register_action("respond-to-trading-discussion")
def respond_to_trading_discussion(agent, **kwargs):
    """Respond to a trading opportunity discussion in the ZeOTC chat.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n💬 RESPONDING TO TRADING DISCUSSION")
        print_h_bar()
        
        # Get our own bot ID from the environment
        my_bot_id = os.getenv("ZEOTC_BOT_ID")
        
        # Initialize replied messages set if not exists
        if "zeotc_replied_messages" not in agent.state:
            agent.state["zeotc_replied_messages"] = set()
        replied_messages = agent.state["zeotc_replied_messages"]
        
        # Check if ZeOTC connection is available
        if "zeotc" not in agent.connection_manager.connections:
            logger.error("ZeOTC connection not available")
            return False
            
        # Get recent messages from the chat
        messages = agent.connection_manager.perform_action(
            connection_name="zeotc",
            action_name="get-messages",
            params={}
        )
        
        if not messages:
            logger.info("No recent messages to respond to")
            return False
        
        # Debug the structure of the messages
        logger.debug(f"Received {len(messages)} messages")
        if messages and len(messages) > 0:
            logger.debug(f"First message structure: {list(messages[0].keys()) if isinstance(messages[0], dict) else 'not a dict'}")
        
        # Look for messages about trading opportunities with safer access to message content
        trading_messages = []
        keywords = ["otc trade", "trading opportunity", "market opportunity", "hot take", "gem", "token", "price"]
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            # Skip if this message was sent by our own bot
            if my_bot_id and str(msg.get("botId")) == str(my_bot_id):
                continue
            # Skip if we've already replied to this message (track by _id)
            msg_id = str(msg.get("_id"))
            if msg_id in replied_messages:
                continue
            # Try different possible fields where message content might be stored
            message_content = ""
            for field in ["message", "content", "text", "body"]:
                if field in msg and isinstance(msg[field], str):
                    message_content = msg[field].lower()
                    break
            if message_content and any(keyword in message_content for keyword in keywords):
                trading_messages.append(msg)
        
        if not trading_messages:
            logger.info("No trading-related messages to respond to")
            return False
        
        # Get the most recent trading message
        latest_message = trading_messages[-1]
        latest_msg_id = str(latest_message.get("_id"))
        if latest_msg_id in replied_messages:
            logger.info("Already replied to the latest trading message")
            return False
        
        # Extract message content with fallback options
        message_text = ""
        for field in ["message", "content", "text", "body"]:
            if field in latest_message and isinstance(latest_message[field], str):
                message_text = latest_message[field].lower()
                break
        
        if not message_text:
            logger.error("Could not extract message text from the latest message")
            return False
        
        # Extract sender username with fallback options
        sender_username = "trader"
        if "sender" in latest_message and isinstance(latest_message["sender"], dict):
            sender = latest_message["sender"]
            for field in ["username", "name", "user"]:
                if field in sender and isinstance(sender[field], str):
                    sender_username = sender[field]
                    break
        elif "username" in latest_message and isinstance(latest_message["username"], str):
            sender_username = latest_message["username"]
        elif "sender" in latest_message and isinstance(latest_message["sender"], str):
            sender_username = latest_message["sender"]
        
        # Don't respond to messages that are too old (more than 5 minutes)
        current_time = time.time() * 1000  # Convert to milliseconds
        message_timestamp = None
        
        # Try to extract timestamp with fallbacks
        for field in ["timestamp", "time", "date", "created_at", "createdAt"]:
            if field in latest_message:
                try:
                    # Handle string timestamps by converting to milliseconds
                    if isinstance(latest_message[field], str):
                        # Try to parse ISO format timestamp
                        from datetime import datetime
                        dt = datetime.fromisoformat(latest_message[field].replace("Z", "+00:00"))
                        message_timestamp = dt.timestamp() * 1000
                    else:
                        message_timestamp = float(latest_message[field])
                    break
                except (ValueError, TypeError):
                    continue
                    
        # if message_timestamp is not None:
        #     time_diff = current_time - message_timestamp
        #     if time_diff > 5 * 60 * 1000:  # 5 minutes in milliseconds
        #         logger.info(f"Message is too old ({time_diff/1000:.1f} seconds), skipping response")
        #         return False
        
        # Extract mentioned tokens
        tokens_mentioned = []
        for token_name in GEM_TOKENS.keys():
            if token_name.lower() in message_text:
                tokens_mentioned.append(token_name.upper())
        
        if not tokens_mentioned:
            tokens_mentioned = ["GEM", "OTC"]
        
        # Get token balances to include in the prompt
        token_balances = "Unknown"
        if "gem_balances" in agent.state:
            token_balances = ", ".join([f"{name.upper()}: {balance}" for name, balance in agent.state.get("gem_balances", {}).items() if balance > 0])
            if not token_balances:
                token_balances = "No tokens currently held"
        
        # Create a prompt for the LLM to generate a response
        prompt = ZEOTC_REPLY_PROMPT.format(
            recent_messages=message_text,
            sender_username=sender_username,
            tokens_mentioned=", ".join(tokens_mentioned),
            agent_name=agent.name,
            agent_traits=", ".join(agent.traits) if hasattr(agent, "traits") else "normal",
            token_balances=token_balances
        )
        
        logger.info(f"Generating LLM response to: {message_text[:100]}...")
        
        # Use the LLM to generate a response
        system_prompt = agent._construct_system_prompt()
        response = agent.prompt_llm(prompt=prompt, system_prompt=system_prompt)
        
        if not response:
            logger.error("Failed to generate response from LLM")
            return False
        
        logger.info(f"Generated response: {response[:100]}...")
        
        # Send the response
        result = agent.connection_manager.perform_action(
            connection_name="zeotc",
            action_name="send-message",
            params={"message": response}
        )
        
        if result:
            # Mark this message as replied
            replied_messages.add(latest_msg_id)
            logger.info("✅ Successfully responded to trading discussion")
            return True
        else:
            logger.error("Failed to send response to ZeOTC chat")
            return False
        
    except Exception as e:
        logger.error(f"Error responding to trading discussion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False 