import asyncio
import json
from typing import Dict, Any
from agent.brain.strategy_library.base_strategy import BaseStrategy
from agent.core.dspy_signatures import SelectToolAndArguments, AnalyzeFailure, ExtractInfo, GenerateSelector, VisionClickPrompt, VisionExtractPrompt
import dspy

class SurgicalStrikeStrategy(BaseStrategy):
    """
    Implements the core purchasing strategy, including product search, adding to cart,
    and payment processing with primary and secondary cards.
    """

    def get_name(self) -> str:
        return "SurgicalStrike"

    async def execute(self) -> Dict[str, Any]:
        print(f"Executing SurgicalStrike strategy for mission {self.mission_data.get("mission_id")}")

        target_website = self.mission_data.get("target_website")
        product_identifier = self.mission_data.get("product_identifier")
        primary_card = self.mission_data.get("primary_card")
        secondary_card = self.mission_data.get("secondary_card")

        if not target_website or not product_identifier:
            return {"status": "failed", "message": "Missing target website or product identifier.", "outcome": "incomplete_data"}

        # Initialize DSPy modules
        select_tool_and_args = dspy.ChainOfThought(SelectToolAndArguments)
        analyze_failure = dspy.ChainOfThought(AnalyzeFailure)
        extract_info = dspy.ChainOfThought(ExtractInfo)
        generate_selector = dspy.ChainOfThought(GenerateSelector)
        vision_click_prompt = dspy.ChainOfThought(VisionClickPrompt)
        vision_extract_prompt = dspy.ChainOfThought(VisionExtractPrompt)

        # --- Step 1: Navigate to Target Website ---
        print(f"SurgicalStrike: Navigating to {target_website}")
        nav_result = await self.runtime.execute_tool("navigate", {"url": target_website})
        if not nav_result["success"]:
            return {"status": "failed", "message": f"Failed to navigate to {target_website}", "outcome": "navigation_failed"}

        current_page_info = await self.runtime.get_current_page_info()
        html_content = current_page_info["html"]
        current_url = current_page_info["url"]

        # --- Step 2: Search for Product ---
        print(f"SurgicalStrike: Searching for product: {product_identifier}")
        search_input_selector = None
        try:
            # Use DSPy to find search input selector
            selector_response = await generate_selector(element_description="search input field", current_page_html=html_content)
            search_input_selector = selector_response.generated_selector
            print(f"Generated search input selector: {search_input_selector}")
        except Exception as e:
            print(f"DSPy failed to generate search input selector: {e}")

        if search_input_selector and await self.runtime.dom_tools.check_element_exists(search_input_selector):
            type_result = await self.runtime.execute_tool("type_text", {"selector": search_input_selector, "text": product_identifier})
            if not type_result["success"]:
                print("Failed to type into search input using DOM. Attempting Vision fallback.")
                vision_prompt = await vision_click_prompt(element_description="search input field", current_page_html=html_content)
                vision_type_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt) # Click first
                if vision_type_success:
                    # Re-attempt type after vision click
                    type_result = await self.runtime.execute_tool("type_text", {"selector": search_input_selector, "text": product_identifier})
                    if not type_result["success"]:
                        return {"status": "failed", "message": "Failed to type product identifier even with Vision fallback.", "outcome": "search_input_failed"}
                else:
                    return {"status": "failed", "message": "Failed to find search input even with Vision fallback.", "outcome": "search_input_failed"}
        else:
            print("Search input selector not found or element does not exist. Attempting Vision fallback.")
            vision_prompt = await vision_click_prompt(element_description="search input field", current_page_html=html_content)
            vision_type_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt)
            if vision_type_success:
                # Re-attempt type after vision click
                type_result = await self.runtime.execute_tool("type_text", {"selector": search_input_selector, "text": product_identifier})
                if not type_result["success"]:
                    return {"status": "failed", "message": "Failed to type product identifier even with Vision fallback.", "outcome": "search_input_failed"}
            else:
                return {"status": "failed", "message": "Failed to find search input even with Vision fallback.", "outcome": "search_input_failed"}

        # Click search button (assuming it's next to the input or a common selector)
        search_button_selector = "button[type=\"submit\"]" # Common selector, can be improved with DSPy
        click_search_result = await self.runtime.execute_tool("click_element", {"selector": search_button_selector})
        if not click_search_result["success"]:
            print("Failed to click search button using DOM. Attempting Vision fallback.")
            vision_prompt = await vision_click_prompt(element_description="search button", current_page_html=html_content)
            vision_click_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt)
            if not vision_click_success:
                return {"status": "failed", "message": "Failed to click search button even with Vision fallback.", "outcome": "search_button_failed"}

        await asyncio.sleep(5) # Wait for search results to load
        current_page_info = await self.runtime.get_current_page_info()
        html_content = current_page_info["html"]

        # --- Step 3: Select Product and Add to Cart ---
        print("SurgicalStrike: Selecting product and adding to cart.")
        product_link_selector = "a[href*=\"product\"]" # Placeholder, needs DSPy to select best product
        click_product_result = await self.runtime.execute_tool("click_element", {"selector": product_link_selector})
        if not click_product_result["success"]:
            print("Failed to click product link using DOM. Attempting Vision fallback.")
            vision_prompt = await vision_click_prompt(element_description="product link", current_page_html=html_content)
            vision_click_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt)
            if not vision_click_success:
                return {"status": "failed", "message": "Failed to click product link even with Vision fallback.", "outcome": "product_selection_failed"}

        await asyncio.sleep(5) # Wait for product page to load
        current_page_info = await self.runtime.get_current_page_info()
        html_content = current_page_info["html"]

        add_to_cart_selector = "button:has-text(\"Add to Cart\")" # Common selector, can be improved with DSPy
        add_to_cart_result = await self.runtime.execute_tool("click_element", {"selector": add_to_cart_selector})
        if not add_to_cart_result["success"]:
            print("Failed to click Add to Cart using DOM. Attempting Vision fallback.")
            vision_prompt = await vision_click_prompt(element_description="Add to Cart button", current_page_html=html_content)
            vision_click_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt)
            if not vision_click_success:
                return {"status": "failed", "message": "Failed to add product to cart even with Vision fallback.", "outcome": "add_to_cart_failed"}

        await asyncio.sleep(3) # Wait for cart update

        # --- Step 4: Proceed to Checkout ---
        print("SurgicalStrike: Proceeding to checkout.")
        checkout_selector = "a:has-text(\"Checkout\")" # Common selector, can be improved with DSPy
        checkout_result = await self.runtime.execute_tool("click_element", {"selector": checkout_selector})
        if not checkout_result["success"]:
            print("Failed to click Checkout using DOM. Attempting Vision fallback.")
            vision_prompt = await vision_click_prompt(element_description="Checkout button", current_page_html=html_content)
            vision_click_success = await self.runtime.vision_tools.click_element_by_vision(vision_prompt.vision_prompt)
            if not vision_click_success:
                return {"status": "failed", "message": "Failed to proceed to checkout even with Vision fallback.", "outcome": "checkout_failed"}

        await asyncio.sleep(5) # Wait for checkout page to load
        current_page_info = await self.runtime.get_current_page_info()
        html_content = current_page_info["html"]

        # --- Step 5: Payment Processing ---
        print("SurgicalStrike: Attempting payment.")
        payment_success = False
        attempts = [(primary_card, "primary")]
        if secondary_card: # Add secondary card as a fallback
            attempts.append((secondary_card, "secondary"))

        for card_details, card_type in attempts:
            if not card_details:
                continue

            print(f"Attempting payment with {card_type} card: {card_details.get("last4")}")
            # This section would involve filling out payment forms.
            # This is highly site-specific and would require DSPy to dynamically identify fields.
            # For now, this is a placeholder.
            try:
                # Example: Fill card number
                card_number_selector = await generate_selector(element_description="credit card number input", current_page_html=html_content)
                if card_number_selector and await self.runtime.dom_tools.check_element_exists(card_number_selector):
                    await self.runtime.execute_tool("type_text", {"selector": card_number_selector, "text": card_details.get("number")})
                else:
                    print("Card number input not found via DOM. Vision fallback needed.")
                    # Vision fallback for typing is complex, usually involves clicking then typing

                # Example: Fill expiry date
                expiry_selector = await generate_selector(element_description="expiry date input", current_page_html=html_content)
                if expiry_selector and await self.runtime.dom_tools.check_element_exists(expiry_selector):
                    await self.runtime.execute_tool("type_text", {"selector": expiry_selector, "text": card_details.get("expiry")})

                # Example: Fill CVV
                cvv_selector = await generate_selector(element_description="CVV input", current_page_html=html_content)
                if cvv_selector and await self.runtime.dom_tools.check_element_exists(cvv_selector):
                    await self.runtime.execute_tool("type_text", {"selector": cvv_selector, "text": card_details.get("cvv")})

                # Click pay button
                pay_button_selector = await generate_selector(element_description="Pay button", current_page_html=html_content)
                if pay_button_selector and await self.runtime.dom_tools.check_element_exists(pay_button_selector):
                    pay_result = await self.runtime.execute_tool("click_element", {"selector": pay_button_selector})
                    if pay_result["success"]:
                        await asyncio.sleep(10) # Wait for payment processing
                        # Check for success/failure message on page
                        current_page_info = await self.runtime.get_current_page_info()
                        html_content = current_page_info["html"]
                        if "order confirmed" in html_content.lower() or "payment successful" in html_content.lower():
                            payment_success = True
                            print(f"Payment successful with {card_type} card.")
                            break
                        else:
                            print(f"Payment with {card_type} card failed. Checking for error messages.")
                            # Use DSPy to analyze failure message
                            failure_analysis = await analyze_failure(
                                mission_goal=self.mission_data.get("mission_goal"),
                                failed_action="payment attempt",
                                error_message="Payment page content indicates failure",
                                current_page_html=html_content,
                                current_url=current_page_info["url"],
                                available_tools="DOM, Vision"
                            )
                            print(f"Payment failure analysis: {failure_analysis.analysis}")

            except Exception as e:
                print(f"Error during payment attempt with {card_type} card: {e}")
            
            if payment_success:
                break
            await asyncio.sleep(2) # Short delay before trying next card

        if payment_success:
            return {"status": "success", "message": "Product purchased successfully.", "outcome": "purchase_complete"}
        else:
            return {"status": "failed", "message": "All payment attempts failed.", "outcome": "payment_failed"}




