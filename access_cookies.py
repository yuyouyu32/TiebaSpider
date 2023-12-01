from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_baidu_tieba_cookies():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1024,768")
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://tieba.baidu.com/")

    input("请在浏览器中完成登录验证，然后按回车键继续...")

    driver.get("https://tieba.baidu.com/")  # 访问百度贴吧首页以获取 cookies

    cookies = {cookie["name"]: cookie["value"] for cookie in driver.get_cookies()}
    driver.quit()

    return cookies

if __name__ == "__main__":
    cookies = get_baidu_tieba_cookies()
    print("获取到的 cookies：", cookies)
    