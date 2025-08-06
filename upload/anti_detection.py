# ghost_cell/src/anti_detection.py

import time
import random
from playwright.sync_api import Page, Locator

class StealthArmor:
    def __init__(self, page: Page):
        self.page = page

    def human_like_wait(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        wait_time = random.uniform(min_seconds, max_seconds)
        time.sleep(wait_time)

    def slow_human_typing(self, locator: Locator, text: str, delay_range: tuple = (0.05, 0.15)):
        locator.click()
        self.human_like_wait(0.5, 1.0)
        
        for char in text:
            locator.type(char)
            time.sleep(random.uniform(*delay_range))

    def natural_click(self, locator: Locator, timeout: int = 10000):
        try:
            locator.wait_for(state="visible", timeout=timeout)
            
            box = locator.bounding_box()
            if not box:
                locator.click()
                return

            target_x = box['x'] + random.uniform(0.2, 0.8) * box['width']
            target_y = box['y'] + random.uniform(0.2, 0.8) * box['height']
            
            self.page.mouse.move(target_x, target_y, steps=random.randint(8, 15))
            self.human_like_wait(0.3, 0.8)
            
            self.page.mouse.down()
            time.sleep(random.uniform(0.05, 0.15))
            self.page.mouse.up()
            
            print(f"✅ StealthArmor: Naturally clicked element.")
        except Exception as e:
            print(f"❌ StealthArmor: Natural click failed: {e}. Falling back to standard click.")
            locator.click(timeout=timeout)

    def handle_cookie_banner(self):
        try:
            cookie_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("OK")',
                'button:has-text("I Agree")',
                '[id*="cookie"] button',
                '[class*="cookie"] button'
            ]
            
            for selector in cookie_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.is_visible(timeout=2000):
                        self.natural_click(element)
                        print("✅ StealthArmor: Handled cookie banner.")
                        self.human_like_wait(1, 2)
                        break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ StealthArmor: Cookie banner handling failed: {e}")

    def random_scroll(self):
        scroll_distance = random.randint(200, 800)
        direction = random.choice(["up", "down"])
        
        if direction == "down":
            self.page.mouse.wheel(0, scroll_distance)
        else:
            self.page.mouse.wheel(0, -scroll_distance)
        
        self.human_like_wait(1, 3)

