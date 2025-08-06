import dspy

class PlanMission(dspy.Signature):
    """
    Generates a step-by-step plan to complete a web automation mission.
    """
    mission_goal: str = dspy.InputField(desc="The overall goal of the mission, e.g., 'buy iPhone 15 Pro Max from apple.com'")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    current_url: str = dspy.InputField(desc="The current URL of the web page.")
    available_tools: str = dspy.InputField(desc="A list of available tools (DOM, Vision) and their capabilities.")
    plan: str = dspy.OutputField(desc="A detailed, numbered, step-by-step plan to achieve the mission goal. Each step should specify the tool to use and its arguments. If a DOM selector is needed, specify it. If a Vision description is needed, specify it. Prioritize DOM tools. If a step involves sensitive information like credit card details, specify a placeholder like [CARD_NUMBER] or [CVV].")

class SelectToolAndArguments(dspy.Signature):
    """
    Selects the best tool and its arguments based on the current situation and the overall plan.
    """
    current_plan_step: str = dspy.InputField(desc="The current step from the overall mission plan.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    current_url: str = dspy.InputField(desc="The current URL of the web page.")
    available_tools: str = dspy.InputField(desc="A list of available tools (DOM, Vision) and their capabilities.")
    tool_name: str = dspy.OutputField(desc="The name of the tool to use (e.g., 'navigate', 'click_element', 'type_text', 'solve_captcha', 'click_element_by_vision').")
    tool_arguments: str = dspy.OutputField(desc="A JSON string of arguments for the selected tool. E.g., {"selector": "#login-button"} or {"url": "https://example.com"} or {"target_description": "Add to Cart button"}.")

class AnalyzeFailure(dspy.Signature):
    """
    Analyzes why a previous action failed and suggests a new approach or modification to the plan.
    """
    mission_goal: str = dspy.InputField(desc="The overall goal of the mission.")
    failed_action: str = dspy.InputField(desc="The action that was attempted and failed.")
    error_message: str = dspy.InputField(desc="The error message or observation from the failed action.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page after the failure.")
    current_url: str = dspy.InputField(desc="The current URL of the web page after the failure.")
    available_tools: str = dspy.InputField(desc="A list of available tools (DOM, Vision) and their capabilities.")
    analysis: str = dspy.OutputField(desc="An analysis of why the action failed, including potential reasons (e.g., selector changed, element not visible, CAPTCHA).")
    new_plan_step: str = dspy.OutputField(desc="A revised plan step or a new approach to overcome the failure. Specify the tool and its arguments. If DOM selector failed, suggest Vision tool.")

class ExtractInfo(dspy.Signature):
    """
    Extracts specific information from the current web page HTML.
    """
    information_to_extract: str = dspy.InputField(desc="The specific information to extract, e.g., 'product price', 'order confirmation number', 'Trust Score on the page'.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    extracted_info: str = dspy.OutputField(desc="The extracted information in plain text.")

class SummarizePage(dspy.Signature):
    """
    Summarizes the key content and interactive elements of the current web page.
    """
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    summary: str = dspy.OutputField(desc="A concise summary of the page's purpose and main interactive elements (buttons, forms, links).")

class GenerateSelector(dspy.Signature):
    """
    Generates a robust CSS selector for a given element description from the current page HTML.
    """
    element_description: str = dspy.InputField(desc="A description of the element, e.g., 'Add to Cart button', 'Login form', 'Search input field'.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    generated_selector: str = dspy.OutputField(desc="A robust CSS selector for the described element. If multiple elements match, provide the most specific one.")

class VisionClickPrompt(dspy.Signature):
    """
    Generates a concise prompt for the Vision model to identify and click an element.
    """
    element_description: str = dspy.InputField(desc="A description of the element to click, e.g., 'Add to Cart button', 'Next button in the CAPTCHA'.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    vision_prompt: str = dspy.OutputField(desc="A concise, clear prompt for the Vision model to identify the element for clicking. E.g., 'Find and click the blue 'Add to Cart' button'.")

class VisionExtractPrompt(dspy.Signature):
    """
    Generates a concise prompt for the Vision model to extract text from an image.
    """
    information_to_extract: str = dspy.InputField(desc="The specific information to extract, e.g., 'the CAPTCHA text', 'the order confirmation number'.")
    current_page_html: str = dspy.InputField(desc="The current HTML content of the web page.")
    vision_prompt: str = dspy.OutputField(desc="A concise, clear prompt for the Vision model to extract the information. E.g., 'What is the text shown in the image?'.")


