from fastapi import FastAPI
import time
import json
from playwright.sync_api import sync_playwright

app = FastAPI()

@app.get("/")
def health():
    return {"status": "alive"}

@app.get("/search/{case_number}")
def search(case_number: str):
    return lookup_case(case_number)

def lookup_case(case_number):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        page.goto(
            "https://www.dallascounty.org/jaillookup/search.jsp",
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.wait_for_timeout(3000)
        page.mouse.wheel(0, 1500)
        time.sleep(2)

        page.wait_for_selector('input[name="caseNumber"]', timeout=30000)
        page.fill('input[name="caseNumber"]', case_number)

        page.click('input[value="Search By Case Number"]')
        page.wait_for_load_state("networkidle")
        time.sleep(3)

        text = page.inner_text("body")

        if "No records were found" in text:
            browser.close()
            return {"found": False}

        browser.close()
        return {
            "found": True,
            "raw_text": text.strip()
        }
