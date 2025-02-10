from flask import Flask, jsonify, request
import asyncio
from pyppeteer import launch
import nest_asyncio
import logging
import random
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nest_asyncio.apply()
app = Flask(__name__)

# 存储知乎 cookies
ZHIHU_COOKIES = None

def parse_cookie_string(cookie_str):
    """解析 cookie 字符串为对象数组"""
    cookies = []
    for cookie in cookie_str.split(';'):
        cookie = cookie.strip()
        if cookie:
            name, value = cookie.split('=', 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.zhihu.com'
            })
    return cookies

@app.route('/')
def home():
    return "Welcome to Search API"

@app.route('/set_cookies', methods=['POST'])
def set_cookies():
    global ZHIHU_COOKIES
    try:
        # 支持两种格式：字符串格式和对象数组格式
        data = request.json
        if isinstance(data, str):
            ZHIHU_COOKIES = parse_cookie_string(data)
        elif isinstance(data, dict) and 'cookies' in data:
            if isinstance(data['cookies'], str):
                ZHIHU_COOKIES = parse_cookie_string(data['cookies'])
            else:
                ZHIHU_COOKIES = data['cookies']
        else:
            ZHIHU_COOKIES = data
            
        logger.info(f"成功设置 {len(ZHIHU_COOKIES)} 个 cookies")
        return jsonify({"message": "Cookies 设置成功", "count": len(ZHIHU_COOKIES)})
    except Exception as e:
        logger.error(f"设置 cookies 失败: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/search')
def search():
    query = request.args.get('q', 'python')  # 获取搜索关键词，默认为 python
    logger.info(f"开始处理搜索请求: {query}")
    if not ZHIHU_COOKIES:
        return jsonify({"error": "请先设置知乎 cookies"}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(do_search(query))
        logger.info(f"搜索完成，结果: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"搜索过程发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

async def do_search(query):
    logger.info("启动浏览器")
    browser = await launch(
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
        args=[
            '--no-sandbox',
            '--disable-gpu',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--no-zygote',
            '--single-process',
            '--disable-web-security'
        ],
        headless=True,
        dumpio=True
    )
    logger.info("浏览器启动成功")
    
    page = await browser.newPage()
    
    # 设置浏览器特征
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    await page.setViewport({'width': 1920, 'height': 1080})
    
    # 注入 cookies
    logger.info("注入知乎 cookies")
    for cookie in ZHIHU_COOKIES:
        await page.setCookie(cookie)
    
    # 设置请求拦截
    await page.setRequestInterception(True)
    
    async def intercept_request(request):
        if request.resourceType in ['image', 'stylesheet', 'font']:
            await request.abort()
        else:
            await request.continue_()
    
    page.on('request', lambda req: asyncio.ensure_future(intercept_request(req)))
    
    search_results = []
    
    try:
        # 直接访问搜索页面
        search_url = f'https://www.zhihu.com/search?type=content&q={query}'
        logger.info(f"开始访问知乎搜索页面: {search_url}")
        response = await page.goto(search_url, {
            'waitUntil': 'networkidle0',
            'timeout': 30000
        })
        logger.info(f"页面加载状态: {response.status}")
        
        # 随机延时
        await page.waitFor(random.randint(1000, 2000))
        
        # 等待搜索结果加载
        content_selector = '.SearchResult-Card'
        await page.waitForSelector(content_selector, {'timeout': 10000})
        logger.info("搜索结果页面加载完成")

        # 获取搜索结果
        cards = await page.querySelectorAll(content_selector)
        logger.info(f"找到 {len(cards)} 个搜索结果")
        
        for index, card in enumerate(cards[:5], 1):
            try:
                # 提取标题和链接
                title = await page.evaluate('(element) => element.querySelector(".ContentItem-title").innerText', card)
                link = await page.evaluate('(element) => element.querySelector("a").href', card)
                # 提取摘要
                excerpt = await page.evaluate('(element) => element.querySelector(".Highlight").innerText', card)
                
                result_text = f"{index}. {title}\n链接：{link}\n摘要：{excerpt}"
                logger.info(f"提取第 {index} 个结果: {result_text}")
                search_results.append(result_text)
            except Exception as e:
                logger.error(f"提取第 {index} 个结果时出错: {str(e)}")
        
        return search_results
    except Exception as e:
        logger.error(f"搜索过程发生异常: {str(e)}", exc_info=True)
        return ["搜索过程发生错误，请稍后重试"]
    finally:
        logger.info("关闭浏览器")
        await browser.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)