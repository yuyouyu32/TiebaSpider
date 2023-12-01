from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from lxml import etree
import time
import json
from config import cookies, post_link_file, log_file, headers
from urllib.parse import urlparse, parse_qs



def get_pn_value(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'pn' in query_params:
        return query_params['pn'][0]
    else:
        return None
    

def get_post_info_with_cookies(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1024,768")

        # for key, value in headers.items():
        #     chrome_options.add_argument(f'{key}={value}')
        driver = webdriver.Chrome(options=chrome_options)
        

        driver.get("https://tieba.baidu.com/")
        for cookie_name, cookie_value in cookies.items():
            driver.add_cookie({"name": cookie_name, "value": cookie_value})

        driver.get(url)  # 访问贴吧 URL

        # 必要时等待页面加载完成
        time.sleep(1)
        response_txt = driver.page_source
        while '百度安全验证' in response_txt:
            input(f'百度安全验证! {url}， 验证完毕后按回车继续')
            for cookie_name, cookie_value in cookies.items():
                driver.add_cookie({"name": cookie_name, "value": cookie_value})
            driver.get(url)
            time.sleep(1)            
            response_txt = driver.page_source

        html = etree.HTML(response_txt)
        # 标题列表
        title_list = html.xpath('//div[@class="threadlist_title pull_left j_th_tit "]/a[1]/@title')
        # 链接列表
        link_list = html.xpath('//div[@class="threadlist_title pull_left j_th_tit "]/a[1]/@href')
        
        for i in range(len(title_list)):
            item = dict()
            item['title'] = title_list[i]
            item['link'] = 'https://tieba.baidu.com' + link_list[i]
            item['content'] = item['title']
            # 保存帖子数据
            with open(post_link_file, 'a+', encoding='utf-8') as file:
                json_str = json.dumps(item, ensure_ascii=False)
                file.write(json_str + '\n')
        nex_page = html.xpath('//a[@class="next pagination-item "]/@href')
        with open(log_file, 'a+', encoding='utf-8') as file:
            file.write(f'Done in:{url} \n')
        if len(nex_page) > 0:
            next_url = 'https:' + nex_page[0]
            driver.quit()
            pn = get_pn_value(url)
            if pn and int(pn)> 8000:
                return
            get_post_info_with_cookies(next_url)
    except:
        with open(log_file, 'a+', encoding='utf-8') as file:
            file.write(f'Error in:{url} \n')

if __name__ == "__main__":
    url = "https://tieba.baidu.com/f?kw=%E5%89%91%E4%B8%8E%E8%BF%9C%E5%BE%81&ie=utf-8&pn=7900"
    get_post_info_with_cookies(url)