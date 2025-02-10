import requests
import json

# 服务器地址
BASE_URL = 'https://render-demo-selenium-app.onrender.com'

def test_api():
    # 知乎 cookies
    cookies = '_xsrf=uZ15KPSZPWWTdCnEuXixHaYmkvgARlFg; _zap=a20b0eb5-b916-447f-8a81-044ef4adaf9e; d_c0=AADSRU-DiRmPTgWG6PwxO0X1zWFcfNoDZfU=|1731505066; q_c1=dd628d1c9d934bc9b62fed808d493f1c|1739172066000|1739172066000; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1738914845,1738918722,1739033289,1739172069; HMACCOUNT=F9E1C1F954F61F3F; tst=r; z_c0=2|1:0|10:1739172070|4:z_c0|80:MS4xV1VwdEJnQUFBQUFtQUFBQVlBSlZUZWIybG1qd29zdWNSUHQ1OS13X2EtR2pUUDM0RE05WFFnPT0=|c7b896db62ac5763e9ebaeba3c1d621943b46e2053d4493937070d3950ed99a9; __zse_ck=004_xbNypI95KzpMMYIA=fzkj1bTX4sTpVKpwj3ydM6UhLzyAKaSJwkv9mwcH6K3b96VW7vK0RHC/1p=JsBIpG57rtNj6Rv2=vOtjFfKpmMDtLpR/IQyjMgTCQJ=WQANx=Bs-qr16FAvuTowAsxmHhDdl4sDpThdcP0/hveo7/gWmFFjXYlHeA9ca+6ktcidtmkxXcrqN7t85P7ANAF+Uc9DHCtzBx9noXNOcU758KsNqeoaonWeC7xIUjzgl8H55IHIYYBK2NY8saBl72+zVsUoydwJWWpw0ccDwucKz9BNwVL0=; BEC=92a0fca0e2e4d1109c446d0a990ad863; SESSIONID=28ztpXjNRq5sYzXSR8IHNAuboLdwa1fUmAUPpPcqXm3; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1739192639; JOID=VVgUBEy6IFhcYP5fdboXjOeq8s9qjxkkKBChND3oVmwpOYQAJ4Pe9ztn-Fhz-QczppaWlPhQM1Zp478GtdRgkfA=; osd=Ul0WB0y9JVpfYPlad7kXi-Ko8c9tihsnKBekNj7oUWkrOoQHIoHd9zxi-ltz_gIxpZaRkfpTM1Fs4bwGstFikvA='

    print("1. 测试首页...")
    response = requests.get(f"{BASE_URL}/")
    print(f"首页响应: {response.text}\n")

    print("2. 设置 cookies...")
    response = requests.post(
        f"{BASE_URL}/set_cookies",
        json=cookies,
        headers={'Content-Type': 'application/json'}
    )
    print(f"设置 cookies 响应: {response.json()}\n")

    print("3. 测试搜索...")
    search_query = "Python"
    print(f"搜索关键词: {search_query}")
    response = requests.get(f"{BASE_URL}/search", params={'q': search_query})
    
    if response.status_code == 200:
        results = response.json()
        print("\n搜索结果:")
        for result in results:
            print(f"\n{result}")
    else:
        print(f"搜索失败: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_api() 