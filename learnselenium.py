from flask import Flask, jsonify
import asyncio
from pyppeteer import launch
import nest_asyncio
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nest_asyncio.apply()
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Search API"

@app.route('/search')
def search():
    logger.info("开始处理搜索请求")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(do_search())
        logger.info(f"搜索完成，结果: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"搜索过程发生错误: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        loop.close()

async def do_search():
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
        logger.info("开始访问百度")
        response = await page.goto('https://www.baidu.com', {
            'waitUntil': 'networkidle0',
            'timeout': 30000
        })
        logger.info(f"页面加载状态: {response.status}")
        
        # 随机延时
        await page.waitFor(random.randint(1000, 2000))
        
        logger.info("等待搜索框加载")
        await page.waitForSelector('#kw', {'timeout': 10000})
        logger.info("搜索框加载完成")
        
        logger.info("输入搜索关键词")
        # 模拟人类输入
        for char in "python":
            await page.type('#kw', char)
            await page.waitFor(random.randint(50, 150))
        
        await page.waitFor(random.randint(500, 1000))
        await page.keyboard.press('Enter')
        
        logger.info("等待搜索结果加载")
        try:
            # 首先检查是否出现验证码
            captcha_selector = '#wappass-captcha-iframe'
            await page.waitForSelector(captcha_selector, {'timeout': 5000})
            logger.error("检测到验证码，搜索失败")
            return ["检测到验证码，请稍后重试"]
        except Exception:
            # 如果没有验证码，继续等待搜索结果
            await page.waitForSelector('.c-container', {'timeout': 10000})
            logger.info("搜索结果页面加载完成")

            results = await page.querySelectorAll('.c-container')
            logger.info(f"找到 {len(results)} 个搜索结果")
            
            for index, result in enumerate(results[:5], 1):
                try:
                    title = await page.evaluate('(element) => element.querySelector("h3").innerText', result)
                    logger.info(f"提取第 {index} 个结果: {title}")
                    search_results.append(f"{index}. {title}")
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