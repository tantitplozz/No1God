import asyncio
import random
from playwright.async_api import Page

class StealthArmor:
    """
    StealthArmor class to implement human-like browsing behaviors and evade bot detection.
    Includes advanced techniques for fingerprinting evasion and behavioral mimicry.
    """

    def __init__(self, page: Page):
        self.page = page

    async def human_like_scroll(self):
        """
        Performs human-like scrolling behavior with variable speeds and pauses.
        """
        scroll_height = await self.page.evaluate("document.body.scrollHeight")
        current_scroll = 0
        while current_scroll < scroll_height:
            scroll_amount = random.randint(100, 300)
            await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            current_scroll += scroll_amount
            await asyncio.sleep(random.uniform(0.5, 1.5))
            scroll_height = await self.page.evaluate("document.body.scrollHeight") # Update scroll height in case of lazy loading

    async def human_like_typing(self, selector: str, text: str):
        """
        Types text with human-like delays, potential typos, and backspaces.
        """
        await self.page.click(selector) # Focus on the element
        for char in text:
            await self.page.type(selector, char, delay=random.randint(50, 150))
            if random.random() < 0.02: # 2% chance of a typo
                await self.page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await self.page.type(selector, random.choice("abcdefghijklmnopqrstuvwxyz"), delay=random.randint(50, 150))
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await self.page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.1, 0.3))
        await asyncio.sleep(random.uniform(0.5, 1.0))

    async def human_like_click(self, selector: str):
        """
        Clicks an element with human-like mouse movements and delays.
        """
        # Get element bounding box
        box = await self.page.locator(selector).bounding_box()
        if not box:
            raise ValueError(f"Element with selector {selector} not found.")

        # Move mouse to a random point within the element
        x = box["x"] + random.uniform(0, box["width"])
        y = box["y"] + random.uniform(0, box["height"])

        await self.page.mouse.move(x, y, steps=random.randint(5, 15))
        await asyncio.sleep(random.uniform(0.2, 0.8))
        await self.page.mouse.click(x, y)
        await asyncio.sleep(random.uniform(0.5, 1.5))

    async def set_random_user_agent(self):
        """
        Sets a random, common user agent to avoid detection.
        """
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        await self.page.set_extra_http_headers({"User-Agent": random.choice(user_agents)})

    async def evade_fingerprinting(self):
        """
        Applies various techniques to evade common browser fingerprinting methods.
        Includes more advanced JavaScript injection for stealth.
        """
        # Bypass common bot detection scripts by modifying browser properties
        await self.page.evaluate("""
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
              get: () => [
                { name: 'Chrome PDF Plugin', description: 'Portable Document Format', filename: 'internal-pdf-viewer', length: 1 },
                { name: 'Chrome PDF Viewer', description: '', filename: 'mhjfbmdgcfjbbgblmbkgbho mhgnmop', length: 1 }
              ]
            });
            Object.defineProperty(navigator, 'languages', {
              get: () => ['en-US', 'en']
            });
            // Mimic WebGL fingerprinting by providing a consistent, common renderer
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) { // UNMASKED_RENDERER_WEBGL
                    return 'ANGLE (Intel, Intel(R) Iris(R) Xe Graphics (0x000046A6) Direct3D11 vs_5_0 ps_5_0, D3D11)';
                }
                if (parameter === 37446) { // UNMASKED_VENDOR_WEBGL
                    return 'Google Inc.';
                }
                return getParameter(parameter);
            };
            // Mimic Canvas fingerprinting by adding noise
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                const context = this.getContext('2d');
                if (context) {
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {
                        imageData.data[i] += Math.floor(Math.random() * 5); // Add small random noise to red channel
                    }
                    context.putImageData(imageData, 0, 0);
                }
                return toDataURL.apply(this, arguments);
            };
        """)

    async def apply_stealth(self):
        """
        Applies all stealth techniques.
        """
        await self.set_random_user_agent()
        await self.evade_fingerprinting()
        # Add more stealth measures here




