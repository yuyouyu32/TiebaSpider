import requests
from selenium import webdriver
import string
import zipfile
from config import cookies


def create_proxyauth_extension(tunnelhost, tunnelport, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件

    args:
        tunnelhost (str): 你的代理地址或者域名（str类型）
        tunnelport (int): 代理端口号（int类型）
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径

    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=tunnelhost,
        port=tunnelport,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


# 获取代理服务器
def get_proxy_request():
    url = "https://dps.kdlapi.com/api/getdps/?secret_id=ovoeovfi1nyiwhwmnepw&num=1&signature=2jryogfaaput78oyw0i0n0twstkhf9i1&pt=1&sep=1"
    
    response = requests.get(url)
    if response.status_code == 200:
        proxy = response.text.strip()
        return proxy
    else:
        return None
    

def get_driver_proxy(proxy, use_password=False):
    if use_password:
        proxy_ip = proxy.split(":")[0]
        proxy_port = proxy.split(":")[1]
        proxyauth_plugin_path = create_proxyauth_extension(
            tunnelhost=f"{proxy_ip}",  # 隧道域名
            tunnelport=f"{proxy_port}",  # 端口号
            proxy_username="17806277543",  # 用户名
            proxy_password="bestmDxin@3"  # 密码
        )
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension(proxyauth_plugin_path)
        # chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(options=chrome_options)
    else:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--proxy-server={proxy}")
        driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_req_proxy(proxy):
    username = "17806277543"
    password = "bestmDxin@3"
    proxies = {
    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy},
    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy}
    }
    return proxies