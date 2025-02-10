from flask import Flask, jsonify
import asyncio
from pyppeteer import launch
import nest_asyncio

nest_asyncio.apply()
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Search API"

@app.route('/search')
def search():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(do_search())
        return jsonify(result)
    finally:
        loop.close()

async def do_search():
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        args=['--no-sandbox']
    )
    page = await browser.newPage()
    
    try:
        await page.goto('https://www.baidu.com')
        await page.type('#kw', 'python')
        await page.keyboard.press('Enter')
        await page.waitForNavigation()

        results = await page.querySelectorAll('.c-container')
        search_results = []
        for index, result in enumerate(results[:5], 1):
            title = await page.evaluate('(element) => element.querySelector("h3").innerText', result)
            search_results.append(f"{index}. {title}")
        
        return search_results
    finally:
        await browser.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)