import asyncio
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from agent.core.stealth_armor import StealthArmor

class ToolsetDOM:
    """
    ToolsetDOM provides methods for interacting with web elements using DOM selectors.
    """

    def __init__(self, page: Page, stealth_armor: StealthArmor):
        self.page = page
        self.stealth_armor = stealth_armor

    async def navigate(self, url: str) -> bool:
        """
        Navigates to a given URL.
        """
        try:
            await self.page.goto(url, wait_until="domcontentloaded")
            await self.stealth_armor.apply_stealth()
            return True
        except PlaywrightTimeoutError:
            print(f"Navigation to {url} timed out.")
            return False
        except Exception as e:
            print(f"Error navigating to {url}: {e}")
            return False

    async def click_element(self, selector: str) -> bool:
        """
        Clicks an element identified by a CSS selector with human-like behavior.
        """
        try:
            await self.stealth_armor.human_like_click(selector)
            return True
        except PlaywrightTimeoutError:
            print(f"Clicking element {selector} timed out.")
            return False
        except Exception as e:
            print(f"Error clicking element {selector}: {e}")
            return False

    async def type_text(self, selector: str, text: str) -> bool:
        """
        Types text into an input field identified by a CSS selector with human-like behavior.
        """
        try:
            await self.stealth_armor.human_like_typing(selector, text)
            return True
        except PlaywrightTimeoutError:
            print(f"Typing into element {selector} timed out.")
            return False
        except Exception as e:
            print(f"Error typing into element {selector}: {e}")
            return False

    async def get_text(self, selector: str) -> str | None:
        """
        Gets the text content of an element identified by a CSS selector.
        """
        try:
            element = await self.page.locator(selector).first.text_content()
            return element.strip() if element else None
        except PlaywrightTimeoutError:
            print(f"Getting text from element {selector} timed out.")
            return None
        except Exception as e:
            print(f"Error getting text from element {selector}: {e}")
            return None

    async def get_attribute(self, selector: str, attribute: str) -> str | None:
        """
        Gets the value of an attribute from an element identified by a CSS selector.
        """
        try:
            attr_value = await self.page.locator(selector).first.get_attribute(attribute)
            return attr_value
        except PlaywrightTimeoutError:
            print(f"Getting attribute {attribute} from element {selector} timed out.")
            return None
        except Exception as e:
            print(f"Error getting attribute {attribute} from element {selector}: {e}")
            return None

    async def check_element_exists(self, selector: str) -> bool:
        """
        Checks if an element identified by a CSS selector exists on the page.
        """
        try:
            return await self.page.locator(selector).count() > 0
        except Exception as e:
            print(f"Error checking element existence for {selector}: {e}")
            return False

    async def get_page_html(self) -> str:
        """
        Gets the full HTML content of the current page.
        """
        return await self.page.content()

    async def take_screenshot(self, path: str) -> None:
        """
        Takes a screenshot of the current page.
        """
        try:
            await self.page.screenshot(path=path)
        except Exception as e:
            print(f"Error taking screenshot to {path}: {e}")

    async def scroll_to_bottom(self):
        """
        Scrolls to the bottom of the page with human-like behavior.
        """
        await self.stealth_armor.human_like_scroll()

    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """
        Waits for an element identified by a CSS selector to appear.
        """
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            print(f"Element {selector} did not appear within {timeout}ms.")
            return False
        except Exception as e:
            print(f"Error waiting for selector {selector}: {e}")
            return False

    async def get_all_links(self) -> list[str]:
        """
        Gets all unique links (href attributes) from the current page.
        """
        links = await self.page.evaluate("""
            Array.from(document.querySelectorAll("a")).map(a => a.href)
        """)
        return list(set([link for link in links if link]))

    async def get_all_buttons(self) -> list[dict]:
        """
        Gets all button elements with their text and selectors.
        """
        buttons = await self.page.evaluate("""
            Array.from(document.querySelectorAll("button, input[type=\"submit\"], a[role=\"button\"]")).map((el, index) => ({
                text: el.innerText || el.value || el.ariaLabel || el.title,
                selector: `[data-automation-id=\"button-${index}\"]` || `#${el.id}` || `.${el.className.split(" ")[0]}` || el.tagName.toLowerCase(),
                # More robust selector generation would be needed here
            }));
        """)
        # This is a simplified selector generation. In a real scenario, you'd want to generate robust, unique selectors.
        # For now, we'll just return what we get from the browser.
        return buttons

    async def get_form_fields(self, form_selector: str) -> list[dict]:
        """
        Gets all input, select, and textarea fields within a given form selector.
        """
        fields = await self.page.evaluate(f"""
            Array.from(document.querySelectorAll("{form_selector} input, {form_selector} select, {form_selector} textarea")).map(el => ({
                name: el.name,
                id: el.id,
                type: el.type,
                value: el.value,
                placeholder: el.placeholder,
                selector: `#${el.id}` || `[name=\"${el.name}\"]` || `.${el.className.split(" ")[0]}` || el.tagName.toLowerCase(),
            }));
        """)
        return fields




