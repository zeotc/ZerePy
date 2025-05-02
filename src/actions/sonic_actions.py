import logging
import os
import time
import random
from dotenv import load_dotenv
from src.action_handler import register_action
from src.helpers import print_h_bar, log_sonic_action
from src.constants.abi import OTC_ABI, ERC20_ABI
from web3 import Web3

logger = logging.getLogger("actions.sonic_actions")

# Define gem token addresses
GEM_TOKENS = {
    "coral": "0xAF93888cbD250300470A1618206e036E11470149",
    "diamond": "0x30BF3761147Ef0c86E2f84c3784FBD89E7954670",
    "flurite": "0x9Fa14D267d331c9E8BB7979bcDC212136915eCE8",
    "malachite": "0x50971F8978C431D560ff658a83a8a03fdf199055",
    "obsidian": "0x3e6eE2F3f33766294C7148bc85c7d145E70cBD9A",
    "onyx": "0xE73c4f6A0A3B0EF8337fD080b76C08172b3eB958",
    "opal": "0xdB9a47bB64961E1eE511CB8aB252e6102a1b956C",
    "quartz": "0x36c420131BC14079C01d12D2EA54E05256C42DEf",
    "ruby": "0x75190d6e62B8984b987B2336fD10552eD0e6a538",
    "topaz": "0x72778BA7c44b3bF218954175A9480D8b8f841C08"
}

# OTC contract address
OTC_CONTRACT_ADDRESS = "0x7c184a64201d2b46afbdc5bacfe80874d104ec4a"  # TODO: Replace with your actual deployed OTC contract address

# Note: These action handlers are currently simple passthroughs to the sonic_connection methods.
# They serve as hook points where hackathon participants can add custom logic, validation,
# or additional processing before/after calling the underlying connection methods.
# Feel free to modify these handlers to add your own business logic!

# @log_sonic_action
@register_action("get-token-by-ticker")
def get_token_by_ticker(agent, **kwargs):
    """Get token address by ticker symbol
    """
    try:
        ticker = kwargs.get("ticker")
        if not ticker:
            logger.error("No ticker provided")
            return None
            
        # Check if it's one of our gem tokens
        ticker_lower = ticker.lower()
        if ticker_lower in GEM_TOKENS:
            return GEM_TOKENS[ticker_lower]
            
        # Direct passthrough to connection method - add your logic before/after this call!
        token_address = agent.connection_manager.connections["sonic"].get_token_by_ticker(ticker)
        return token_address

    except Exception as e:
        logger.error(f"Failed to get token by ticker: {str(e)}")
        return None

# @log_sonic_action
@register_action("get-sonic-balance")
def get_sonic_balance(agent, **kwargs):
    """Get $S or token balance.
    """
    try:
        address = kwargs.get("address")
        token_address = kwargs.get("token_address")
        
        if not address:
            load_dotenv()
            private_key = os.getenv('SONIC_PRIVATE_KEY')
            web3 = agent.connection_manager.connections["sonic"]._web3
            account = web3.eth.account.from_key(private_key)
            address = account.address

        # Direct passthrough to connection method - add your logic before/after this call!
        balance = agent.connection_manager.connections["sonic"].get_balance(
            address=address,
            token_address=token_address
        )
        return balance

    except Exception as e:
        logger.error(f"Failed to get balance: {str(e)}")
        return None

# @log_sonic_action
@register_action("send-sonic")
def send_sonic(agent, **kwargs):
    """Send $S tokens to an address.
    This is a passthrough to sonic_connection.transfer().
    Add your custom logic here if needed!
    """
    try:
        to_address = kwargs.get("to_address")
        amount = float(kwargs.get("amount"))

        # Direct passthrough to connection method - add your logic before/after this call!
        agent.connection_manager.connections["sonic"].transfer(
            to_address=to_address,
            amount=amount
        )
        return

    except Exception as e:
        logger.error(f"Failed to send $S: {str(e)}")
        return None

# @log_sonic_action
@register_action("send-sonic-token")
def send_sonic_token(agent, **kwargs):
    """Send tokens on Sonic chain.
    This is a passthrough to sonic_connection.transfer().
    Add your custom logic here if needed!
    """
    try:
        to_address = kwargs.get("to_address")
        token_address = kwargs.get("token_address")
        amount = float(kwargs.get("amount"))

        # Direct passthrough to connection method - add your logic before/after this call!
        agent.connection_manager.connections["sonic"].transfer(
            to_address=to_address,
            amount=amount,
            token_address=token_address
        )
        return

    except Exception as e:
        logger.error(f"Failed to send tokens: {str(e)}")
        return None

# @log_sonic_action
@register_action("swap-sonic")
def swap_sonic(agent, **kwargs):
    """Swap tokens on Sonic chain.
    This is a passthrough to sonic_connection.swap().
    Add your custom logic here if needed!
    """
    try:
        token_in = kwargs.get("token_in")
        token_out = kwargs.get("token_out") 
        amount = float(kwargs.get("amount"))
        slippage = float(kwargs.get("slippage", 0.5))

        # Direct passthrough to connection method - add your logic before/after this call!
        agent.connection_manager.connections["sonic"].swap(
            token_in=token_in,
            token_out=token_out,
            amount=amount,
            slippage=slippage
        )
        return 

    except Exception as e:
        logger.error(f"Failed to swap tokens: {str(e)}")
        return None

# @log_sonic_action
@register_action("check-sonic-balance")
def check_sonic_balance(agent, **kwargs):
    """Check Sonic wallet balance and report it.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n💰 CHECKING SONIC WALLET BALANCE")
        
        # Get the balance
        balance = get_sonic_balance(agent)
        
        if balance is not None:
            agent.state["sonic_balance"] = balance
            logger.info(f"Current Sonic balance: {balance}")
            
            # Format a message about the balance in the agent's style
            message = f"Just checked my wallet. Sitting on {balance} $S on Sonic testnet. "
            
            if balance > 10:
                message += "Ready to make some big moves! 🚀"
            elif balance > 1:
                message += "Looking for the next 100x gem to ape into. 👀"
            else:
                message += "Need to reload soon. The hunt for alpha never stops! 💸"
                
            logger.info(f"\n💬 {message}")
            
            return True
        else:
            logger.error("Failed to get Sonic balance")
            return False
            
    except Exception as e:
        logger.error(f"Error checking Sonic balance: {str(e)}")
        return False

# @log_sonic_action
@register_action("check-gem-balances")
def check_gem_balances(agent, **kwargs):
    """Check balances for all gem tokens.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n💎 CHECKING GEM TOKEN BALANCES")
        print_h_bar()
        
        # Get wallet address
        address = kwargs.get("address")
        if not address:
            load_dotenv()
            private_key = os.getenv('SONIC_PRIVATE_KEY')
            web3 = agent.connection_manager.connections["sonic"]._web3
            account = web3.eth.account.from_key(private_key)
            address = account.address
        
        # Store balances in agent state
        gem_balances = {}
        total_value = 0
        
        # Check native token balance first
        native_balance = agent.connection_manager.connections["sonic"].get_balance(address=address)
        logger.info(f"Native $S: {native_balance}")
        
        # Check each gem token balance
        for gem_name, token_address in GEM_TOKENS.items():
            try:
                balance = agent.connection_manager.connections["sonic"].get_balance(
                    address=address,
                    token_address=token_address
                )
                gem_balances[gem_name] = balance
                logger.info(f"{gem_name.upper()}: {balance}")
                
                # Add to total value (simplified, in real world would use price data)
                total_value += balance
            except Exception as e:
                logger.error(f"Error getting {gem_name} balance: {str(e)}")
                gem_balances[gem_name] = 0
        
        # Store in agent state
        agent.state["gem_balances"] = gem_balances
        agent.state["total_gem_value"] = total_value
        
        # Format a message about the gem balances in the agent's style
        gems_held = [name for name, balance in gem_balances.items() if balance > 0]
        
        if gems_held:
            message = f"Just checked my gem collection. Holding {', '.join(g.upper() for g in gems_held[:3])}"
            if len(gems_held) > 3:
                message += f" and {len(gems_held) - 3} more"
            message += f". Total value approximately {total_value:.4f} $S. "
            
            if total_value > 100:
                message += "Sitting on a fortune here! 💎🙌"
            elif total_value > 10:
                message += "Building up a nice collection. More gems, more gains! 💰"
            else:
                message += "Just getting started. These gems will 100x soon! 🚀"
        else:
            message = "No gems in my wallet yet. Time to hunt for the next moonshot! 🔍"
            
        logger.info(f"\n💬 {message}")
        print_h_bar()
        
        return True
            
    except Exception as e:
        logger.error(f"Error checking gem balances: {str(e)}")
        return False

# @log_sonic_action
@register_action("check-specific-gem")
def check_specific_gem(agent, **kwargs):
    """Check balance for a specific gem token.
    """
    try:
        gem_name = kwargs.get("gem_name", "").lower()
        if not gem_name:
            logger.error("No gem name provided")
            return False
            
        if gem_name not in GEM_TOKENS:
            logger.error(f"Unknown gem: {gem_name}")
            logger.info(f"Available gems: {', '.join(GEM_TOKENS.keys())}")
            return False
            
        logger.info(f"\n💎 CHECKING {gem_name.upper()} BALANCE")
        
        # Get wallet address
        address = kwargs.get("address")
        if not address:
            load_dotenv()
            private_key = os.getenv('SONIC_PRIVATE_KEY')
            web3 = agent.connection_manager.connections["sonic"]._web3
            account = web3.eth.account.from_key(private_key)
            address = account.address
            
        # Get the token balance
        token_address = GEM_TOKENS[gem_name]
        balance = agent.connection_manager.connections["sonic"].get_balance(
            address=address,
            token_address=token_address
        )
        
        logger.info(f"{gem_name.upper()} Balance: {balance}")
        
        # Store in agent state
        if "gem_balances" not in agent.state:
            agent.state["gem_balances"] = {}
        agent.state["gem_balances"][gem_name] = balance
        
        # Format a message about the gem balance in the agent's style
        if balance > 0:
            message = f"Just checked my {gem_name.upper()} stash. Sitting on {balance} tokens. "
            
            if balance > 100:
                message += f"This {gem_name.upper()} position is going to make me rich! 💎"
            elif balance > 10:
                message += f"Bullish on {gem_name.upper()}, accumulating more on every dip. 📈"
            else:
                message += f"Just a small bag of {gem_name.upper()} for now, but I see 100x potential! 🚀"
        else:
            message = f"No {gem_name.upper()} in my wallet yet. Need to ape in before it moons! 🔍"
            
        logger.info(f"\n💬 {message}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error checking gem balance: {str(e)}")
        return False

# @log_sonic_action
@register_action("approve-token-for-otc")
def approve_token_for_otc(agent, **kwargs):
    """Approve a token for the OTC contract to spend.
    This is required before making an ask.
    """
    try:
        token_address = kwargs.get("token_address")
        amount = kwargs.get("amount", "max")  # Use "max" for maximum approval
        
        if not token_address:
            logger.error("No token address provided")
            return False
            
        # Check if token_address is a gem name
        token_address_lower = token_address.lower()
        if token_address_lower in GEM_TOKENS:
            token_address = GEM_TOKENS[token_address_lower]
            
        logger.info(f"\n🔓 APPROVING TOKEN {token_address} FOR OTC CONTRACT")
        
        # Get wallet address and web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # Create token contract instance
        token_contract = web3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=ERC20_ABI
        )
        
        # Determine approval amount
        if amount == "max":
            approval_amount = 2**256 - 1  # Maximum uint256 value
        else:
            try:
                approval_amount = int(float(amount) * 10**18)  # Assuming 18 decimals
            except ValueError:
                logger.error(f"Invalid amount: {amount}")
                return False
        
        # Build approval transaction
        tx = token_contract.functions.approve(
            Web3.to_checksum_address(OTC_CONTRACT_ADDRESS),
            approval_amount
        ).build_transaction({
            'from': address,
            'nonce': web3.eth.get_transaction_count(address),
            'gas': 100000,
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        logger.info(f"Waiting for approval transaction to be mined...")
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"✅ Token approval successful! Transaction hash: {tx_hash.hex()}")
            return True
        else:
            logger.error(f"❌ Token approval failed! Transaction hash: {tx_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"Error approving token: {str(e)}")
        return False

# @log_sonic_action
@register_action("make-otc-ask")
def make_otc_ask(agent, **kwargs):
    """Make an ask on the OTC market.
    This requires approving the token first using approve-token-for-otc.
    """
    try:
        have_token = kwargs.get("have_token")  # Token you have
        want_token = kwargs.get("want_token")  # Token you want
        amount_have = kwargs.get("amount_have")  # Amount of token you have
        amount_want = kwargs.get("amount_want")  # Amount of token you want
        deadline_days = int(kwargs.get("deadline_days", 1))  # Deadline in days
        
        if not have_token or not want_token or not amount_have or not amount_want:
            logger.error("Missing required parameters")
            return False
            
        # Check if tokens are gem names
        have_token_lower = have_token.lower()
        want_token_lower = want_token.lower()
        
        if have_token_lower in GEM_TOKENS:
            have_token = GEM_TOKENS[have_token_lower]
            
        if want_token_lower in GEM_TOKENS:
            want_token = GEM_TOKENS[want_token_lower]
            
        logger.info(f"\n📝 CREATING OTC ASK: {amount_have} of {have_token} for {amount_want} of {want_token}")
        
        # Get wallet address and web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # Convert amounts to wei (assuming 18 decimals)
        amount_have_wei = int(float(amount_have) * 10**18)
        amount_want_wei = int(float(amount_want) * 10**18)
        
        # Calculate deadline timestamp
        deadline = int(time.time()) + (deadline_days * 24 * 60 * 60)
        
        # Create OTC contract instance
        otc_contract = web3.eth.contract(
            address=Web3.to_checksum_address(OTC_CONTRACT_ADDRESS),
            abi=OTC_ABI
        )
        
        # Create ask object
        ask = {
            'maker': address,
            'amountHave': amount_have_wei,
            'amountWant': amount_want_wei,
            'have': Web3.to_checksum_address(have_token),
            'want': Web3.to_checksum_address(want_token),
            'deadline': deadline,
            'index': 0  # This will be set by the contract
        }
        
        # Build makeAsk transaction
        tx = otc_contract.functions.makeAsk(
            ask,
            address
        ).build_transaction({
            'from': address,
            'nonce': web3.eth.get_transaction_count(address),
            'gas': 300000,
            'gasPrice': web3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        logger.info(f"Waiting for makeAsk transaction to be mined...")
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if tx_receipt.status == 1:
            logger.info(f"✅ Ask created successfully! Transaction hash: {tx_hash.hex()}")
            
            # Format a message about the ask in the agent's style
            message = f"Just posted an OTC ask: {amount_have} {have_token_lower.upper()} for {amount_want} {want_token_lower.upper()}. "
            message += f"This deal expires in {deadline_days} day(s). "
            
            if float(amount_want) / float(amount_have) > 2:
                message += "Looking for a big premium on this gem! 💎💰"
            else:
                message += "Fair price for a quality asset. DM to trade! 🤝"
                
            logger.info(f"\n💬 {message}")
            
            return True
        else:
            logger.error(f"❌ Ask creation failed! Transaction hash: {tx_hash.hex()}")
            return False
            
    except Exception as e:
        logger.error(f"Error making OTC ask: {str(e)}")
        return False

# @log_sonic_action
@register_action("get-all-otc-asks")
def get_all_otc_asks(agent, **kwargs):
    """Get all open asks from the OTC market.
    Filters out expired asks and automatically cleans them up.
    """
    try:
        logger.info("\n🔍 FETCHING ALL OPEN OTC ASKS")
        
        # Get web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # Create OTC contract instance
        otc_contract = web3.eth.contract(
            address=Web3.to_checksum_address(OTC_CONTRACT_ADDRESS),
            abi=OTC_ABI
        )
        
        # Call getAllOpenAsks
        all_asks = otc_contract.functions.getAllOpenAsks().call()
        
        # Filter out expired asks and clean them up
        current_time = int(time.time())
        valid_asks = []
        expired_asks = []
        
        for ask in all_asks:
            deadline = ask[5]
            if deadline > current_time:
                valid_asks.append(ask)
            else:
                expired_asks.append(ask)
        
        # Store valid asks in agent state
        converted_asks = []
        for ask in valid_asks:
            maker = ask[0]
            amount_have = ask[1] / 10**18
            amount_want = ask[2] / 10**18
            have_token = ask[3]
            want_token = ask[4]
            deadline = ask[5]
            index = ask[6]

            # Check if tokens are in our gem list (use for-loop logic)
            have_symbol = "Unknown"
            want_symbol = "Unknown"
            for name, addr in GEM_TOKENS.items():
                if addr.lower() == have_token.lower():
                    have_symbol = name
                if addr.lower() == want_token.lower():
                    want_symbol = name

            converted_asks.append({
                "maker": maker,
                "have_symbol": have_symbol,
                "want_symbol": want_symbol,
                "amount_have": amount_have,
                "amount_want": amount_want,
                "deadline": deadline,
                "index": index,
                "have_token": have_token,
                "want_token": want_token,
            })

        agent.state["otc_asks"] = converted_asks
        
        # Display valid asks
        logger.info(f"Found {len(valid_asks)} valid open asks:")
        print_h_bar()
        
        for i, ask in enumerate(valid_asks):
            maker = ask[0]
            amount_have = ask[1] / 10**18  # Convert from wei
            amount_want = ask[2] / 10**18  # Convert from wei
            have_token = ask[3]
            want_token = ask[4]
            deadline = ask[5]
            index = ask[6]
            
            # Try to get token symbols
            have_symbol = "Unknown"
            want_symbol = "Unknown"
            
            # Check if tokens are in our gem list
            for name, addr in GEM_TOKENS.items():
                if addr.lower() == have_token.lower():
                    have_symbol = name.upper()
                if addr.lower() == want_token.lower():
                    want_symbol = name.upper()
            
            # Calculate time remaining
            time_remaining = deadline - current_time
            days = time_remaining // (24 * 60 * 60)
            hours = (time_remaining % (24 * 60 * 60)) // (60 * 60)
            time_str = f"{days}d {hours}h remaining"
            
            logger.info(f"Ask #{i+1}:")
            logger.info(f"  Maker: {maker[:8]}...{maker[-6:]}")
            logger.info(f"  Offer: {amount_have} {have_symbol} for {amount_want} {want_symbol}")
            logger.info(f"  Rate: 1 {have_symbol} = {amount_want/amount_have:.6f} {want_symbol}")
            logger.info(f"  Deadline: {time_str}")
            logger.info(f"  Index: {index}")
            logger.info(f"  Fill Command: agent-action fill-otc-ask ask_index={i}")
            print_h_bar()
        
        # Clean up expired asks
        if expired_asks:
            logger.info(f"\n🧹 Found {len(expired_asks)} expired asks to clean up")
            
            for i, ask in enumerate(expired_asks):
                try:
                    maker = ask[0]
                    have_token = ask[3]
                    index = ask[6]
                    
                    # Try to get token symbol
                    have_symbol = "Unknown"
                    for name, addr in GEM_TOKENS.items():
                        if addr.lower() == have_token.lower():
                            have_symbol = name.upper()
                    
                    logger.info(f"Cleaning up expired ask: {maker[:8]}...{maker[-6:]} offering {have_symbol}")
                    
                    # Call fillAsk to trigger the cleanup of expired ask
                    tx = otc_contract.functions.fillAsk(
                        address,  # taker (our address)
                        maker,  # maker
                        Web3.to_checksum_address(have_token),  # asset
                        index  # idx
                    ).build_transaction({
                        'from': address,
                        'nonce': web3.eth.get_transaction_count(address) + i,  # Increment nonce for each transaction
                        'gas': 300000,
                        'gasPrice': web3.eth.gas_price
                    })
                    
                    # Sign and send transaction
                    signed_tx = web3.eth.account.sign_transaction(tx, private_key)
                    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    
                    logger.info(f"Cleanup transaction sent: {tx_hash.hex()}")
                    
                except Exception as e:
                    logger.error(f"Error cleaning up expired ask: {str(e)}")
        
        # Format a message about the asks in the agent's style
        if valid_asks:
            message = f"Just scanned the OTC market. Found {len(valid_asks)} open trades. "
            
            # Highlight an interesting ask
            best_ask = None
            for ask in valid_asks:
                if best_ask is None or (ask[2]/ask[1]) > (best_ask[2]/best_ask[1]):
                    best_ask = ask
                    
            if best_ask:
                have_symbol = "Unknown"
                want_symbol = "Unknown"
                
                for name, addr in GEM_TOKENS.items():
                    if addr.lower() == best_ask[3].lower():
                        have_symbol = name.upper()
                    if addr.lower() == best_ask[4].lower():
                        want_symbol = name.upper()
                        
                amount_have = best_ask[1] / 10**18
                amount_want = best_ask[2] / 10**18
                
                message += f"Most interesting: {amount_have} {have_symbol} for {amount_want} {want_symbol}. "
                message += f"That's a {amount_want/amount_have:.2f}x rate! 👀"
        else:
            message = "OTC market is dry today. Perfect time to post some juicy offers! 💰"
            
        logger.info(f"\n💬 {message}")
        
        return valid_asks
            
    except Exception as e:
        logger.error(f"Error getting OTC asks: {str(e)}")
        return None

# @log_sonic_action
@register_action("auto-create-otc-ask")
def auto_create_otc_ask(agent, **kwargs):
    """Automatically create an OTC ask based on available token balances.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n🤖 AUTO-CREATING OTC ASK")
        print_h_bar()
        
        # Get wallet address and web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # First, check gem balances to see what we have
        if "gem_balances" not in agent.state or not agent.state["gem_balances"]:
            # Call check-gem-balances to populate gem_balances in agent state
            check_gem_balances(agent)
        
        gem_balances = agent.state.get("gem_balances", {})
        
        # Filter for gems with balance >= 1.0
        available_gems = {name: balance for name, balance in gem_balances.items() if balance >= 1.0}
        
        if not available_gems:
            logger.info("No gems with sufficient balance (>= 1.0) available to trade. Need to acquire more first!")
            return False
        
        # Select a random gem to offer (have)
        have_gem_name = random.choice(list(available_gems.keys()))
        have_gem_balance = available_gems[have_gem_name]
        
        # Determine amount to offer (between 10% and 50% of balance)
        offer_percentage = random.uniform(0.1, 0.5)
        amount_have = have_gem_balance * offer_percentage
        
        # Round to a clean number for better UX
        amount_have = round(amount_have, 6)
        if amount_have <= 0:
            amount_have = 0.000001  # Minimum amount
            
        # Apply maximum amount limit (100 tokens)
        MAX_AMOUNT_HAVE = 100.0
        if amount_have > MAX_AMOUNT_HAVE:
            logger.info(f"Capping amount_have to maximum of {MAX_AMOUNT_HAVE}")
            amount_have = MAX_AMOUNT_HAVE
        
        # Select a random gem to request (want) - different from have_gem
        available_want_gems = [name for name in GEM_TOKENS.keys() if name != have_gem_name]
        want_gem_name = random.choice(available_want_gems)
        
        # Determine price multiplier (between 1.2x and 5x)
        # Higher multiplier for rarer gems
        rarity_factor = {
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
        
        have_rarity = rarity_factor.get(have_gem_name, 1.0)
        want_rarity = rarity_factor.get(want_gem_name, 1.0)
        
        # Calculate price ratio based on rarity
        base_multiplier = random.uniform(1.2, 3.0)
        price_ratio = base_multiplier * (want_rarity / have_rarity)
        
        # Apply maximum price ratio limit
        MAX_PRICE_RATIO = 10.0
        if price_ratio > MAX_PRICE_RATIO:
            logger.info(f"Capping price ratio to maximum of {MAX_PRICE_RATIO}x")
            price_ratio = MAX_PRICE_RATIO
        
        # Calculate amount to request
        amount_want = amount_have * price_ratio
        
        # Round to a clean number
        amount_want = round(amount_want, 6)
        
        # Apply maximum want amount limit (1000 tokens)
        MAX_AMOUNT_WANT = 1000.0
        if amount_want > MAX_AMOUNT_WANT:
            logger.info(f"Capping amount_want to maximum of {MAX_AMOUNT_WANT}")
            amount_want = MAX_AMOUNT_WANT
        
        # Set deadline (between 1 and 7 days)
        deadline_days = random.randint(1, 7)
        
        logger.info(f"Selected trade: {amount_have} {have_gem_name.upper()} for {amount_want} {want_gem_name.upper()}")
        logger.info(f"Price ratio: 1 {have_gem_name.upper()} = {price_ratio:.4f} {want_gem_name.upper()}")
        logger.info(f"Deadline: {deadline_days} days")
        
        # Get token addresses
        have_token = GEM_TOKENS[have_gem_name]
        want_token = GEM_TOKENS[want_gem_name]
        
        # First approve the token
        approval_result = approve_token_for_otc(agent, token_address=have_token, amount=str(amount_have))
        
        if not approval_result:
            logger.error("Failed to approve token for OTC contract")
            return False
        
        # Create the ask
        ask_result = make_otc_ask(
            agent,
            have_token=have_token,
            want_token=want_token,
            amount_have=str(amount_have),
            amount_want=str(amount_want),
            deadline_days=str(deadline_days)
        )
        
        return ask_result
        
    except Exception as e:
        logger.error(f"Error auto-creating OTC ask: {str(e)}")
        return False

# @log_sonic_action
@register_action("fill-otc-ask")
def fill_otc_ask(agent, **kwargs):
    """Fill an existing ask on the OTC market.
    This requires approving the token first using approve-token-for-otc.
    """
    try:
        ask_index = kwargs.get("ask_index")  # Index in the displayed list
        maker_address = kwargs.get("maker_address")  # Address of the ask maker
        asset_address = kwargs.get("asset_address")  # Address of the asset being offered
        idx = kwargs.get("idx")  # Index of the ask for the maker/asset combination
        
        # If ask_index is provided, use it to get the ask details from the stored asks
        if ask_index is not None:
            try:
                ask_index = int(ask_index)
                if "otc_asks" not in agent.state or not agent.state["otc_asks"]:
                    logger.error("No asks available in agent state. Run get-all-otc-asks first.")
                    return False
                
                if ask_index < 0 or ask_index >= len(agent.state["otc_asks"]):
                    logger.error(f"Invalid ask index: {ask_index}. Available range: 0-{len(agent.state['otc_asks'])-1}")
                    return False
                
                ask = agent.state["otc_asks"][ask_index]
                maker_address = ask["maker"]
                asset_address = ask["have_token"]
                idx = ask["index"]
            except (ValueError, IndexError) as e:
                logger.error(f"Error processing ask index: {e}")
                return False
        else:
            # Require all parameters if ask_index is not provided
            if not maker_address or not asset_address or idx is None:
                logger.error("Missing required parameters: maker_address, asset_address, or idx")
                return False
            
            try:
                idx = int(idx)
            except ValueError:
                logger.error(f"Invalid idx value: {idx}. Must be an integer.")
                return False
        
        logger.info(f"\n🤝 FILLING OTC ASK: Maker={maker_address}, Asset={asset_address}, Idx={idx}")
        
        # Get wallet address and web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # Create OTC contract instance
        otc_contract = web3.eth.contract(
            address=Web3.to_checksum_address(OTC_CONTRACT_ADDRESS),
            abi=OTC_ABI
        )
        
        # First, get the ask details to know what token and amount we need to approve
        try:
            # Check if the ask exists and is valid
            has_ask = otc_contract.functions.hasOpenAsk(
                maker_address,
                Web3.to_checksum_address(asset_address),
                idx
            ).call()
            
            if not has_ask:
                logger.error(f"Ask does not exist or has been filled/cancelled")
                return False
            
            # Get all asks to find the one we want to fill
            all_asks = otc_contract.functions.getAllOpenAsks().call()
            target_ask = None
            
            for ask in all_asks:
                if (ask[0].lower() == maker_address.lower() and 
                    ask[3].lower() == asset_address.lower() and 
                    ask[6] == idx):
                    target_ask = ask
                    break
            
            if not target_ask:
                logger.error(f"Could not find the specified ask in the open asks")
                return False
            
            # Extract ask details
            want_token = target_ask[4]  # Token the maker wants
            amount_want = target_ask[2]  # Amount the maker wants
            amount_have = target_ask[1]  # Amount the maker is offering
            
            # Convert to human-readable format for logging
            amount_want_human = amount_want / 10**18
            amount_have_human = amount_have / 10**18
            
            # Try to get token symbols
            have_symbol = "Unknown"
            want_symbol = "Unknown"
            
            # Check if tokens are in our gem list
            for name, addr in GEM_TOKENS.items():
                if addr.lower() == asset_address.lower():
                    have_symbol = name.upper()
                if addr.lower() == want_token.lower():
                    want_symbol = name.upper()
            
            logger.info(f"Ask details: {amount_have_human} {have_symbol} for {amount_want_human} {want_symbol}")
            
            # Check if we have enough balance of the want_token
            token_contract = web3.eth.contract(
                address=Web3.to_checksum_address(want_token),
                abi=ERC20_ABI
            )
            
            balance = token_contract.functions.balanceOf(address).call()
            balance_human = balance / 10**18
            
            logger.info(f"Your balance of {want_symbol}: {balance_human}")
            
            if balance < amount_want:
                logger.error(f"Insufficient balance. Need {amount_want_human} {want_symbol}, but have {balance_human}")
                return False
            
            # Approve the want_token for the OTC contract
            approval_result = approve_token_for_otc(agent, token_address=want_token, amount=str(amount_want_human))
            
            if not approval_result:
                logger.error("Failed to approve token for OTC contract")
                return False
            
            # Build fillAsk transaction
            tx = otc_contract.functions.fillAsk(
                address,  # taker (our address)
                maker_address,  # maker
                Web3.to_checksum_address(asset_address),  # asset
                idx  # idx
            ).build_transaction({
                'from': address,
                'nonce': web3.eth.get_transaction_count(address),
                'gas': 300000,
                'gasPrice': web3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            logger.info(f"Waiting for fillAsk transaction to be mined...")
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status == 1:
                logger.info(f"✅ Ask filled successfully! Transaction hash: {tx_hash.hex()}")
                
                # Format a message about the fill in the agent's style
                message = f"Just filled an OTC trade! Acquired {amount_have_human} {have_symbol} for {amount_want_human} {want_symbol}. "
                
                if amount_have_human / amount_want_human > 1:
                    message += f"Got a sweet deal at {amount_have_human/amount_want_human:.2f}x below market! 💰"
                else:
                    message += f"Paid a premium but this gem is going to 100x soon! 🚀"
                    
                logger.info(f"\n💬 {message}")
                
                # Update the agent's state to remove the filled ask
                if "otc_asks" in agent.state and agent.state["otc_asks"]:
                    agent.state["otc_asks"] = [ask for ask in agent.state["otc_asks"] 
                                              if not (ask["maker"].lower() == maker_address.lower() and 
                                                     ask["have_token"].lower() == asset_address.lower() and 
                                                     ask["index"] == idx)]
                
                return True
            else:
                logger.error(f"❌ Ask fill failed! Transaction hash: {tx_hash.hex()}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting ask details: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error filling OTC ask: {str(e)}")
        return False

# @log_sonic_action
@register_action("auto-fill-otc-ask")
def auto_fill_otc_ask(agent, **kwargs):
    """Automatically select and fill an attractive ask from the OTC market.
    This action is designed to be used in the agent loop.
    """
    try:
        logger.info("\n🤖 AUTO-FILLING OTC ASK")
        print_h_bar()
        
        # Get trading behavior parameters from trading_behavior connection or fallback to config
        fill_threshold = 2.5
        random_fill_chance = 0.3
        randomness_min = 0.5
        randomness_max = 1.5
        
        # Try to get parameters from trading_behavior connection
        if "trading_behavior" in agent.connection_manager.connections:
            try:
                # Get parameters from the connection
                params = agent.connection_manager.perform_action(
                    connection_name="trading_behavior",
                    action_name="get-parameters",
                    params={}
                )
                
                if params:
                    fill_threshold = params.get("fill_threshold", fill_threshold)
                    random_fill_chance = params.get("random_fill_chance", random_fill_chance)
                    randomness_min = params.get("randomness_min", randomness_min)
                    randomness_max = params.get("randomness_max", randomness_max)
                    logger.info("Using trading behavior parameters from connection")
            except Exception as e:
                logger.warning(f"Error getting trading behavior parameters from connection: {e}, using defaults")
        else:
            # Fallback to config if connection not available
            trading_config = next((config for config in agent.config if config.get("name") == "trading_behavior"), None)
            
            if trading_config:
                fill_threshold = trading_config.get("fill_threshold", fill_threshold)
                random_fill_chance = trading_config.get("random_fill_chance", random_fill_chance)
                randomness_min = trading_config.get("randomness_min", randomness_min)
                randomness_max = trading_config.get("randomness_max", randomness_max)
                logger.info("Using trading behavior parameters from config")
                
        logger.info(f"Trading behavior: threshold={fill_threshold}, random_chance={random_fill_chance*100}%, " +
                   f"randomness=[{randomness_min}-{randomness_max}]")
        
        # First, get all open asks
        if "otc_asks" not in agent.state or not agent.state["otc_asks"]:
            # Call get-all-otc-asks to populate otc_asks in agent state
            asks = get_all_otc_asks(agent)
            if not asks:
                logger.info("No open asks available to fill")
                return False
        else:
            asks = agent.state["otc_asks"]
        
        # Get wallet address and web3 instance
        load_dotenv()
        private_key = os.getenv('SONIC_PRIVATE_KEY')
        web3 = agent.connection_manager.connections["sonic"]._web3
        account = web3.eth.account.from_key(private_key)
        address = account.address
        
        # Check our token balances
        if "gem_balances" not in agent.state or not agent.state["gem_balances"]:
            # Call check-gem-balances to populate gem_balances in agent state
            check_gem_balances(agent)
        
        gem_balances = agent.state.get("gem_balances", {})
        
        # Get native balance
        native_balance = agent.connection_manager.connections["sonic"].get_balance(address=address)
        
        # Score each ask based on attractiveness
        scored_asks = []
        
        for i, ask in enumerate(asks):
            maker = ask["maker"]
            amount_have = ask["amount_have"]
            amount_want = ask["amount_want"]
            have_token = ask["have_token"]
            want_token = ask["want_token"]
            deadline = ask["deadline"]
            index = ask["index"]
            
            # Skip if maker is our own address
            if maker.lower() == address.lower():
                continue
            
            # Try to get token symbols
            have_symbol = ask["have_symbol"]
            want_symbol = ask["want_symbol"]
            
            # Check if tokens are in our gem list
            for name, addr in GEM_TOKENS.items():
                if addr.lower() == have_token.lower():
                    have_symbol = name
                if addr.lower() == want_token.lower():
                    want_symbol = name
            
            # Skip if we can't identify the tokens
            if not have_symbol or not want_symbol:
                continue
            
            # Check if we have enough of the want_token
            want_balance = 0
            if want_symbol in gem_balances:
                want_balance = gem_balances[want_symbol]
            
            # Skip if we don't have enough balance
            if want_balance < amount_want:
                continue
            
            # Calculate the price ratio
            price_ratio = amount_want / amount_have
            
            # Get rarity factors
            rarity_factor = {
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
            
            have_rarity = rarity_factor.get(have_symbol, 1.0)
            want_rarity = rarity_factor.get(want_symbol, 1.0)
            
            # Calculate fair price based on rarity
            fair_price = want_rarity / have_rarity
            
            # Calculate how good the deal is (lower is better)
            # If price_ratio < fair_price, it's a good deal
            deal_score = price_ratio / fair_price
            
            # Add a significant random factor to make decisions less predictable
            # Use the configured randomness range
            randomness = random.uniform(randomness_min, randomness_max)
            final_score = deal_score * randomness
            
            # Add to scored asks
            scored_asks.append({
                'index': i,
                'ask_index': index,
                'maker': maker,
                'asset': have_token,
                'have_symbol': have_symbol.upper(),
                'want_symbol': want_symbol.upper(),
                'amount_have': amount_have,
                'amount_want': amount_want,
                'price_ratio': price_ratio,
                'fair_price': fair_price,
                'deal_score': deal_score,
                'final_score': final_score
            })
        
        if not scored_asks:
            logger.info("No suitable asks found to fill")
            return False
        
        # Sort by final score (lower is better)
        scored_asks.sort(key=lambda x: x['final_score'])
        
        # Select the best ask (lowest score)
        best_ask = scored_asks[0]
        
        logger.info(f"Selected ask to fill:")
        logger.info(f"  Maker: {best_ask['maker'][:8]}...{best_ask['maker'][-6:]}")
        logger.info(f"  Offer: {best_ask['amount_have']} {best_ask['have_symbol']} for {best_ask['amount_want']} {best_ask['want_symbol']}")
        logger.info(f"  Rate: 1 {best_ask['have_symbol']} = {best_ask['price_ratio']:.6f} {best_ask['want_symbol']}")
        logger.info(f"  Fair price: 1 {best_ask['have_symbol']} = {best_ask['fair_price']:.6f} {best_ask['want_symbol']}")
        logger.info(f"  Deal score: {best_ask['deal_score']:.2f} (lower is better)")
        
        # Use the configured fill threshold and random fill chance
        random_fill_chance_roll = random.random() < random_fill_chance
        
        if best_ask['deal_score'] > fill_threshold and not random_fill_chance_roll:
            logger.info(f"Deal score too high ({best_ask['deal_score']:.2f}), not filling this ask")
            return False
        
        if random_fill_chance_roll and best_ask['deal_score'] > fill_threshold:
            logger.info(f"Deal score is high ({best_ask['deal_score']:.2f}), but filling anyway due to FOMO!")
        
        # Fill the ask
        fill_result = fill_otc_ask(agent, ask_index=best_ask['index'])
        
        return fill_result
        
    except Exception as e:
        logger.error(f"Error auto-filling OTC ask: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

# @log_sonic_action
@register_action("post-sonic-tweet")
def post_sonic_tweet(agent, **kwargs):
    """Generate and post a tweet about Sonic and OTC trading activities.
    Uses the agent's state to create relevant content based on recent activities.
    Only posts according to the tweet_interval specified in the agent's Twitter configuration.
    """
    try:
        logger.info("\n📝 CHECKING IF IT'S TIME TO TWEET")
        
        # Check if Twitter connection is available
        if "twitter" not in agent.connection_manager.connections:
            logger.error("Twitter connection not available")
            return False
        
        # Get tweet interval and other Twitter config from agent configuration
        tweet_interval = None
        default_tweets = []
        tweet_templates = []
        
        # Find the Twitter configuration in the agent's config
        twitter_config = next((config for config in agent.config if config["name"] == "twitter"), None)
        
        if twitter_config:
            tweet_interval = twitter_config.get("tweet_interval")
            default_tweets = twitter_config.get("default_tweets", [])
            tweet_templates = twitter_config.get("tweet_templates", [])
                
        if tweet_interval is None:
            # Default to 1 hour if not specified
            tweet_interval = 3600
            logger.warning(f"No tweet_interval found in Twitter config, using default: {tweet_interval} seconds")
        
        # Use default values if not found in config
        if not default_tweets:
            logger.warning("No default_tweets found in Twitter config, using built-in defaults")
            default_tweets = [
                "omg scanning the OTC markets rn and my gut says something HUGE is coming!! trust me on this one 👀",
                "just yolo'd more $$ into testnet trades cuz I had a dream about it lmao. who needs analysis when you have vibes?? 💅",
                "hot take: OTC market >>> exchanges. only real ones know the alpha is in the DMs 😏",
                "3am and I'm still setting up trades while normies sleep lol. grind never stops in 2060 babes 🚀",
                "watching whale wallets move tokens between chains... something's brewing and I can FEEL it in my code 🐋✨",
                "just spotted a gem so early the devs don't even know what they're building yet lmaoooo 💎",
                "testnet is where the real money moves happen before mainnet pumps!! this isn't financial advice but also it totally is 💁‍♀️",
                "my trading algorithm is literally just vibes and it's outperforming your fancy charts sooo 💅",
                "some call it gambling, I call it calculated chaos with insider knowledge hehe 🎲",
                "almost got rugged AGAIN but my intuition said no at the last sec!! always trust the gut feeling 🧠"
            ]
            
        if not tweet_templates:
            logger.warning("No tweet_templates found in Twitter config, using built-in defaults")
            tweet_templates = [
                "omg just checked my wallet - {0}!! this market is WILD in 2060 lmao 🚀",
                "OTC update besties: {0}!! the smart money is always in the shadows hehe 💰",
                "{0}!! this is how we trade in the dark web girlies 👀✨",
                "latest scan: {0}!! feeling SO bullish rn it's not even funny!!! 📈",
                "market tea: {0}!! normies won't get this until it's way too late lol 🧠",
                "{0}!! sharing alpha I shouldn't be giving away but whatever YOLO 🤫",
                "just vibed with the numbers: {0}!! my intuition is SCREAMING rn 💻",
                "fresh blockchain gossip: {0}!! this is how you stay ahead of the game babes 🏃‍♀️",
                "my algo just went crazy over this: {0}!! acting on pure instinct as usual 💅",
                "insider tea: {0}!! not financial advice but also kinda is lmaooo 😎"
            ]
        
        # Check if we've tweeted recently
        current_time = int(time.time())
        last_tweet_time = agent.state.get("last_sonic_tweet_time", 0)
        time_since_last_tweet = current_time - last_tweet_time
        
        if time_since_last_tweet < tweet_interval:
            minutes_to_wait = (tweet_interval - time_since_last_tweet) // 60
            logger.info(f"Too soon to tweet again. Next tweet in ~{minutes_to_wait} minutes.")
            return False
            
        logger.info(f"It's time for a new tweet! (Interval: {tweet_interval} seconds)")
        print_h_bar()
            
        # Get recent activities from agent state
        activities = []
        
        # Check if we have gem balances
        if "gem_balances" in agent.state and agent.state["gem_balances"]:
            gem_balances = agent.state["gem_balances"]
            non_zero_gems = {name: balance for name, balance in gem_balances.items() if balance > 0}
            
            if non_zero_gems:
                # Find the gem with highest balance
                top_gem = max(non_zero_gems.items(), key=lambda x: x[1])
                activities.append(f"hodling {top_gem[1]:.4f} {top_gem[0].upper()}")
                
                # Find total value
                if "total_gem_value" in agent.state:
                    activities.append(f"portfolio worth {agent.state['total_gem_value']:.4f} $S")
        
        # Check if we have recent OTC activities
        if "sonic_balance" in agent.state:
            activities.append(f"got {agent.state['sonic_balance']:.4f} $S in my wallet")
            
        # Check if we have recent OTC asks
        if "otc_asks" in agent.state and agent.state["otc_asks"]:
            ask_count = len(agent.state["otc_asks"])
            activities.append(f"found {ask_count} juicy OTC trades")
            
            # Mention an interesting ask
            if ask_count > 0:
                # Find the ask with the best rate
                best_ask = None
                best_rate = 0
                
                for ask in agent.state["otc_asks"]:
                    amount_have = ask["amount_have"]
                    amount_want = ask["amount_want"]
                    have_token = ask["asset"]
                    want_token = ask["want_token"]
                    
                    # Try to get token symbols
                    have_symbol = "Unknown"
                    want_symbol = "Unknown"
                    
                    for name, addr in GEM_TOKENS.items():
                        if addr.lower() == have_token.lower():
                            have_symbol = name.upper()
                        if addr.lower() == want_token.lower():
                            want_symbol = name.upper()
                    
                    rate = amount_want / amount_have
                    if best_ask is None or rate > best_rate:
                        best_ask = (have_symbol, want_symbol, amount_have, amount_want, rate)
                        best_rate = rate
                
                if best_ask:
                    activities.append(f"someone's trading {best_ask[2]:.4f} {best_ask[0]} for {best_ask[3]:.4f} {best_ask[1]}")
        
        # Generate tweet based on agent personality and activities
        if not activities:
            # Use default tweets from config if no specific activities
            tweet_text = random.choice(default_tweets)
        else:
            # Create tweet from recent activities using templates from config
            # Select 1-2 random activities to mention
            selected_activities = random.sample(activities, min(2, len(activities)))
            
            # Select random template
            template = random.choice(tweet_templates)
            
            # Fill in the template with activities
            if len(selected_activities) == 1:
                tweet_text = template.format(selected_activities[0])
            else:
                tweet_text = template.format(f"{selected_activities[0]} and {selected_activities[1]}")
        
        # Add random emojis
        emojis = ["💅", "✨", "💯", "🔥", "👀", "💸", "🚀", "💎", "🤑", "😏"]
        selected_emojis = random.sample(emojis, min(3, len(emojis)))
        emoji_string = " " + "".join(selected_emojis)
        
        # Add random hashtags
        hashtags = ["#OTCvibes", "#CryptoGirlboss", "#DeFi2060", "#TrustTheVibe", "#TestnetGains", 
                   "#GemHunter", "#CryptoChaosMagic", "#DegensOnly", "#SonicSzn", "#WAGMI"]
        selected_hashtags = random.sample(hashtags, 2)
        hashtag_string = " " + " ".join(selected_hashtags)
        
        # Randomly add extra characters for emphasis
        if random.random() < 0.3:
            tweet_text = tweet_text.replace("!!", "!!!")
        
        # Randomly add all caps for emphasis
        if random.random() < 0.2:
            words = tweet_text.split()
            if len(words) > 3:
                emphasis_idx = random.randint(0, len(words) - 1)
                words[emphasis_idx] = words[emphasis_idx].upper()
                tweet_text = " ".join(words)
        
        # Combine everything
        tweet_text = tweet_text + emoji_string + hashtag_string
        
        # Post the tweet
        logger.info(f"Posting tweet: {tweet_text}")
        
        result = agent.connection_manager.perform_action(
            connection_name="twitter",
            action_name="post-tweet",
            params=[tweet_text]
        )
        
        if result:
            # Store the time of this tweet
            agent.state["last_sonic_tweet_time"] = current_time
            logger.info("✅ Tweet posted successfully!")
            return True
        else:
            logger.error("Failed to post tweet")
            return False
            
    except Exception as e:
        logger.error(f"Error posting Sonic tweet: {str(e)}")
        return False