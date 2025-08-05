"""
Playwright driver abstraction.

This module wraps Playwright to provide methods for loading pages,
extracting DOM snapshots and executing actions. The goal is to
isolate all Playwright‑specific code from the rest of the agent so
that other parts of the system can work at a higher level of
abstraction.

The driver is intentionally skeletal; you'll need to fill in the
implementations using Playwright's API.
"""
from __future__ import annotations

import time
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright, Playwright, Browser, BrowserContext, Page


class BrowserDriver:
    """Wrapper around Playwright for page navigation and interaction."""

    def __init__(self, headless: bool = False) -> None:
        """Initialise the browser session.

        You may wish to call ``playwright.sync_api.sync_playwright`` here
        and set up a persistent context for re‑use across multiple
        applications.

        Args:
            headless: Whether to run the browser in headless mode. For
                debugging you might prefer a visible browser.
        """
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._start_browser()

    def _start_browser(self) -> None:
        """Initialize Playwright browser and context."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def load_page(self, url: str) -> None:
        """Load the given URL in the browser.

        This should navigate to the URL and wait for the page to load
        sufficiently. You may need to wait for network idle or a
        particular element to appear.
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        print(f"Loading page: {url}")
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        time.sleep(2)  # Additional wait for dynamic content

    def get_page_snapshot(self) -> Dict[str, Any]:
        """Return a snapshot of the current page state.

        The snapshot is a dictionary containing at least:

        - ``html``: the full page HTML as a string.
        - ``text``: the visible text content of the page body.
        - ``buttons``: a list of clickable elements, each with an ``id``,
          ``selector`` and ``text``. The ``id`` should be a stable index
          within the current snapshot.
        - ``inputs``: a list of input elements, each with an ``id``,
          ``selector``, ``label`` (if available) and ``type`` (e.g. "text"
          or "file").
        
        You can customise the structure of these lists but they must
        provide enough information for the language model to decide
        which elements to interact with.
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        # Get page content
        html = self.page.content()
        text = self.page.inner_text("body")
        
        # Extract buttons (including Easy Apply button)
        buttons = []
        button_elements = self.page.query_selector_all("button, [role='button'], .jobs-apply-button, .jobs-s-apply")
        for i, element in enumerate(button_elements):
            try:
                text_content = element.inner_text().strip()
                if text_content:  # Only include buttons with text
                    buttons.append({
                        "id": f"btn_{i}",
                        "selector": f"button:nth-of-type({i+1})",
                        "text": text_content,
                        "element": element  # Store for later use
                    })
            except:
                continue
        
        # Extract input fields
        inputs = []
        input_elements = self.page.query_selector_all("input, textarea, select")
        for i, element in enumerate(input_elements):
            try:
                input_type = element.get_attribute("type") or "text"
                label_text = ""
                
                # Try to find associated label
                element_id = element.get_attribute("id")
                if element_id:
                    label = self.page.query_selector(f"label[for='{element_id}']")
                    if label:
                        label_text = label.inner_text().strip()
                
                # If no label found, look for nearby text
                if not label_text:
                    try:
                        parent = element.locator("xpath=..")
                        label_text = parent.inner_text().strip()[:50]  # Limit length
                    except:
                        label_text = element.get_attribute("placeholder") or ""
                
                inputs.append({
                    "id": f"input_{i}",
                    "selector": f"input:nth-of-type({i+1})" if element.tag_name == "input" else f"{element.tag_name}:nth-of-type({i+1})",
                    "label": label_text,
                    "type": input_type,
                    "element": element  # Store for later use
                })
            except:
                continue
        
        return {
            "html": html,
            "text": text,
            "buttons": buttons,
            "inputs": inputs,
        }

    def execute_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute a sequence of actions on the page.

        Each action is a dictionary produced by the language model. The
        following keys may be expected:

        - ``action``: The action type, e.g. ``click``, ``fill``, ``upload``.
        - ``id``: The identifier of the element in the snapshot on which
          to act. You'll need to resolve this to a selector from the
          snapshot previously returned by ``get_page_snapshot``.
        - ``value``: For ``fill`` actions, the text to type into the input.
        - ``file``: For ``upload`` actions, the path of the file to upload.

        Returns a result dictionary that could include a status or other
        diagnostic information.
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")
        
        results = []
        
        for action in actions:
            try:
                action_type = action.get("action")
                element_id = action.get("id")
                
                print(f"Executing action: {action_type} on element {element_id}")
                
                if action_type == "click":
                    # Find the element by its ID from the last snapshot
                    if element_id.startswith("btn_"):
                        btn_index = int(element_id.split("_")[1])
                        buttons = self.page.query_selector_all("button, [role='button'], .jobs-apply-button, .jobs-s-apply")
                        if btn_index < len(buttons):
                            buttons[btn_index].click()
                            time.sleep(1)
                            results.append({"action": action_type, "status": "success"})
                        else:
                            results.append({"action": action_type, "status": "element_not_found"})
                    
                elif action_type == "fill":
                    value = action.get("value", "")
                    if element_id.startswith("input_"):
                        input_index = int(element_id.split("_")[1])
                        inputs = self.page.query_selector_all("input, textarea, select")
                        if input_index < len(inputs):
                            inputs[input_index].fill(value)
                            time.sleep(0.5)
                            results.append({"action": action_type, "status": "success", "value": value})
                        else:
                            results.append({"action": action_type, "status": "element_not_found"})
                
                elif action_type == "upload":
                    file_path = action.get("file", "")
                    if element_id.startswith("input_"):
                        input_index = int(element_id.split("_")[1])
                        inputs = self.page.query_selector_all("input[type='file']")
                        if input_index < len(inputs):
                            inputs[input_index].set_input_files(file_path)
                            time.sleep(1)
                            results.append({"action": action_type, "status": "success", "file": file_path})
                        else:
                            results.append({"action": action_type, "status": "element_not_found"})
                
                else:
                    results.append({"action": action_type, "status": "unknown_action"})
                    
            except Exception as e:
                print(f"Error executing action {action}: {e}")
                results.append({"action": action_type, "status": "error", "error": str(e)})
        
        return {"status": "completed", "results": results}

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def find_easy_apply_button(self) -> Optional[str]:
        """Find the Easy Apply button on the current page."""
        if not self.page:
            return None
        
        # Look for Easy Apply button with various selectors
        selectors = [
            "button:has-text('Easy Apply')",
            ".jobs-s-apply button",
            ".jobs-apply-button",
            "[aria-label*='Easy Apply']",
            "button:has-text('Apply')"
        ]
        
        for selector in selectors:
            try:
                element = self.page.query_selector(selector)
                if element and element.is_visible():
                    return selector
            except:
                continue
        
        return None