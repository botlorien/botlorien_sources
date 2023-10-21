
def run():
    from playwright.sync_api import sync_playwright
    import requests
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://sistema.ssw.inf.br/bin/ssw0422")

        page.fill("input[name='f1']", "otc")
        page.fill("input[name='f2']", "12345678909")
        page.fill("input[name='f3']", "botcvl")
        page.fill("input[name='f4']", "1706")
        page.click("button[type='submit']")
        # maybe wait for some element that appears after login
        # page.wait_for_selector("div.logged-in")

        # Get cookies from Playwright
        cookies_list = page.context.cookies()

        # Close the browser
        browser.close()

        # Convert Playwright cookies format to requests format
        cookies = {cookie["name"]: cookie["value"] for cookie in cookies_list}

        # Use cookies with requests library
        response = requests.get("http://example.com/some-protected-page", cookies=cookies)

        print(response.text)


run()
