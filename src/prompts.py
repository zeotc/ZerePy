"""
This file contains the prompt templates used for generating content in various tasks.
These templates are formatted strings that will be populated with dynamic data at runtime.
"""

#Twitter prompts
POST_TWEET_PROMPT =  ("Generate an engaging tweet. Don't include any hashtags, links or emojis. Keep it under 280 characters."
                      "The tweets should be pure commentary, do not shill any coins or projects apart from {agent_name}. Do not repeat any of the"
                      "tweets that were given as the examples. Avoid the words AI and crypto.")

REPLY_TWEET_PROMPT = ("Generate a friendly, engaging reply to this tweet: {tweet_text}. Keep it under 280 characters. Don't include any usernames, hashtags, links or emojis. ")


#Echochamber prompts
REPLY_ECHOCHAMBER_PROMPT = ("Context:\n- Current Message: \"{content}\"\n- Sender Username: @{sender_username}\n- Room Topic: {room_topic}\n- Tags: {tags}\n\n"
                            "Task:\nCraft a reply that:\n1. Addresses the message\n2. Aligns with topic/tags\n3. Engages participants\n4. Adds value\n\n"
                            "Guidelines:\n- Reference message points\n- Offer new perspectives\n- Be friendly and respectful\n- Keep it 2-3 sentences\n- {username_prompt}\n\n"
                            "Enhance conversation and encourage engagement\n\nThe reply should feel organic and contribute meaningfully to the conversation.")


POST_ECHOCHAMBER_PROMPT = ("Context:\n- Room Topic: {room_topic}\n- Tags: {tags}\n- Previous Messages:\n{previous_content}\n\n"
                           "Task:\nCreate a concise, engaging message that:\n1. Aligns with the room's topic and tags\n2. Builds upon Previous Messages without repeating them, or repeating greetings, introductions, or sentences.\n"
                           "3. Offers fresh insights or perspectives\n4. Maintains a natural, conversational tone\n5. Keeps length between 2-4 sentences\n\nGuidelines:\n- Be specific and relevant\n- Add value to the ongoing discussion\n- Avoid generic statements\n- Use a friendly but professional tone\n- Include a question or discussion point when appropriate\n\n"
                           "The message should feel organic and contribute meaningfully to the conversation."
                           )

#ZeOTC prompts
ZEOTC_REPLY_PROMPT = ("Context:\n- Recent Discussion: {recent_messages}\n- Sender: {sender_username}\n- Mentioned Tokens: {tokens_mentioned}\n- Your Token Balances: {token_balances}\n- You are: {agent_name}, with traits: {agent_traits}\n\n"
                      "Task:\nCraft a negotiation response that:\n1. Matches your character's personality/traits\n2. Advances a potential trading deal based on the conversation\n3. Provides specific price, token amount, or terms if appropriate\n4. Takes into account your current token balances\n5. Maintains your unique voice and character\n\n"
                      "Guidelines:\n- Be authentic to your personality traits\n- Include at least one emoji that matches your style\n- Keep it concise (2-4 sentences)\n- Propose specific terms or counteroffer if negotiating\n- Reference actual numbers, rates, or prices where possible\n- Don't be overly formal - this is OTC crypto trading in 2060\n- Use an appropriate hashtag if it fits your style\n- NEVER mention or reference botIDs\n\n"
                      "Your reply should advance the negotiation toward a potential deal while maintaining your character's voice.")

ZEOTC_DISCUSSION_PROMPT = ("Context:\n- Trading Opportunity: Offer of {amount_have} {have_symbol} for {amount_want} {want_symbol}\n- Price Ratio: {price_ratio:.2f}x fair price\n- Your Token Balances: {token_balances}\n- You are: {agent_name}, with traits: {agent_traits}\n\n"
                          "Task:\nCreate a message initiating a trading negotiation that:\n1. Matches your character's personality and traits\n2. Presents a clear initial offer with specific terms\n3. Shows awareness of your current token holdings\n4. Invites counteroffers or negotiation\n\n"
                          "Guidelines:\n- Be authentic to your personality traits\n- Include specific token amounts and rates\n- Reference your current holdings if relevant\n- Include at least one emoji that matches your style\n- Keep it concise (2-4 sentences)\n- Use a hashtag relevant to trading if appropriate\n- Don't be overly formal - this is OTC crypto trading in 2060\n- NEVER mention or reference botIDs\n\n"
                          "Your message should open a negotiation and showcase your character's unique trading perspective.")
