from flask import Flask, jsonify
import asyncio
from pyppeteer import launch

app = Flask(__name__)

@app.route('/search')
async def search():
    browser = await launch()
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
        
        return jsonify(search_results)
    finally:
        await browser.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)