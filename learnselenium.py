from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time

app = Flask(__name__)

@app.route('/search')
def search():
    # 移除 CHROMEDRIVER_PATH
    service = Service()
    driver = webdriver.Chrome(service=service)

    try:
        driver.get('https://www.baidu.com')
        search_box = driver.find_element(By.ID, 'kw')
        search_box.send_keys('python')
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)

        results = driver.find_elements(By.CSS_SELECTOR, '.c-container')
        search_results = []
        for index, result in enumerate(results[:5], 1):
            title = result.find_element(By.CSS_SELECTOR, 'h3').text
            search_results.append(f"{index}. {title}")
        
        return jsonify(search_results)
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)