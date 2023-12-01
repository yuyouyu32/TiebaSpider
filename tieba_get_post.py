import json
import re
from lxml import etree
import time
import json
from config import cookies, html_files, headers
from urllib.parse import urlparse, parse_qs
from proxy import get_driver_proxy, get_req_proxy
import requests
import random
from tqdm import tqdm
import argparse

def get_tid_from_link(url):
    match = re.search(r"/p/(\d+)", url)
    tid = match.group(1)
    return tid


def get_pn_value(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'pn' in query_params:
        return query_params['pn'][0]
    else:
        return None

class SpiderTieba:
    def __init__(self) -> None:
        self.valid_proxy = "n489.kdltps.com:15818"

    def get_html_from_proxy(self, url, pn, title, use_password=False):
        tid = get_tid_from_link(url)
        done_flag = False
        while not done_flag:
            try:
                driver = get_driver_proxy(self.valid_proxy, use_password)
                driver.get("https://tieba.baidu.com/")
                if "百度贴吧" not in driver.page_source:
                    driver.close()
                    print(f"{url} & pn = {pn} 登录失败")
                    continue
                for cookie_name, cookie_value in cookies.items():
                    driver.add_cookie({"name": cookie_name, "value": cookie_value})
                
                driver.get(url) 

                time.sleep(random.uniform(1,1.5))
                response_txt = driver.page_source
                if "剑与远征" not in response_txt:
                    driver.close()
                    if "该贴已被删除" in response_txt:
                        print(f"{url} & pn = {pn} 该贴已被删除")
                        break
                    print(f"{url} & pn = {pn} 获取html失败")
                    driver.close()
                    continue
                driver.close()
                with open(f"{html_files}/{tid}_{pn}.html", "w", encoding="utf-8") as file:
                    file.write(response_txt)

                comments_url = f"https://tieba.baidu.com/p/totalComment?tid={tid}&pn={pn}"
                comments_rsp = requests.get(comments_url).json()
                with open(f"{html_files}/{tid}_{pn}_comments.json", "w", encoding="utf-8") as file:
                    file.write(json.dumps(comments_rsp, ensure_ascii=False))
                if comments_rsp['errmsg'] != 'success':
                    print(f"{comments_url} 获取评论失败")
                    continue
                done_flag = True
            except Exception as e:
                print(e)
                print(f"{url} & pn = {pn} 获取html失败, 正在尝试下一次连接")

        html = etree.HTML(response_txt)
        return html

    def get_html_from_proxy_request(self, url, pn, title, use_password=False):
        tid = get_tid_from_link(url)
        done_flag = False
        while not done_flag:
            try:
                time.sleep(random.uniform(0.5, 1.2))
                proxys = get_req_proxy(self.valid_proxy)
                response = requests.get(url, proxies=proxys, cookies=cookies, headers=headers)
                # response = requests.get(url, proxies=proxys, timeout=8)
                response_txt = response.text

                if "剑与远征" not in response_txt:
                    if "被删除" in response_txt or "被隐藏" in response_txt:
                        print(f"{url} & pn = {pn} 该贴已被删除 or 被隐藏")
                        break
                    print(f"{url} & pn = {pn} 获取html失败")
                    continue
                with open(f"{html_files}/{tid}_{pn}.html", "w", encoding="utf-8") as file:
                    file.write(response_txt)

                comments_url = f"https://tieba.baidu.com/p/totalComment?tid={tid}&pn={pn}"
                comments_rsp = requests.get(comments_url).json()
                with open(f"{html_files}/{tid}_{pn}_comments.json", "w", encoding="utf-8") as file:
                    file.write(json.dumps(comments_rsp, ensure_ascii=False))

                if comments_rsp['errmsg'] != 'success':
                    print(f"{comments_url} 获取评论失败")
                    continue

                done_flag = True
            except Exception as e:
                print(e)
                print(f"{url} & pn = {pn} 获取html失败, 正在尝试下一次连接")

        html = etree.HTML(response_txt)
        return html
    
    def get_post_html(self, url, title, pn=1, use_request=False):
        
        get_method = self.get_html_from_proxy_request if use_request else self.get_html_from_proxy
        html = get_method(url, pn, title, use_password=True)
        
        nex_page = html.xpath('//div[contains(@class, "pb_footer")]//ul[@class="l_posts_num"]/li[@class="l_pager pager_theme_5 pb_list_pager"]/a/@href')
        nex_page_text = html.xpath('//div[contains(@class, "pb_footer")]//ul[@class="l_posts_num"]/li[@class="l_pager pager_theme_5 pb_list_pager"]/a/text()')

        if "下一页" in nex_page_text:
            index = nex_page_text.index("下一页")
            next_url = 'https://tieba.baidu.com'+nex_page[index]
            pn = get_pn_value(next_url)
            get_method(url=next_url, title=title, pn=pn)


def main(start_index, end_index, post_log):
    with open("post_link.jsonl", "r", encoding="utf-8") as file:
        json_objects = [json.loads(line) for line in file]
    spider = SpiderTieba()
    for index in tqdm(range(start_index, min(end_index, len(json_objects)))):
        json_object = json_objects[index]
        url = json_object['link']
        title = json_object['title']
        spider.get_post_html(url, title, use_request=True)
        with open(post_log, 'a+', encoding='utf-8') as file:
            file.write(f'index: {index} Done in:{url} \n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SpiderTieba Script')
    parser.add_argument('--start_index', type=int, required=True, help='Starting index for processing')
    parser.add_argument('--end_index', type=int, required=True, help='Ending index for processing')
    parser.add_argument('--post_log', type=str, required=True, help='Path to the post_log file')

    args = parser.parse_args()
    main(args.start_index, args.end_index, args.post_log)

        