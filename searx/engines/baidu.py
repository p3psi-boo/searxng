# SPDX-License-Identifier: AGPL-3.0-or-later
"""Baidu is a Chinese multinational technology company specializing in Internet-related services and products and artificial intelligence.

.. Website: https://www.baidu.com
.. Source : https://github.com/ohblue/baidu-serp-api/
"""

import hashlib
import random
import re
import string
import time
from urllib.parse import urlencode
from datetime import datetime, timedelta
import uuid
from lxml import etree

from searx import utils

def gen_random_params():
    bduss = ''.join(random.choices(string.ascii_letters + string.digits, k=176))
    baiduid = uuid.uuid4().hex.upper()[:32]
    isid = uuid.uuid4().hex
    rsv_pq = hex(random.getrandbits(64))
    rsv_t = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
    rsv_sid = '_'.join([str(random.randint(60000, 60300)) for _ in range(6)])
    clist = uuid.uuid4().hex
    _cr1 = hashlib.md5(str(random.getrandbits(128)).encode('utf-8')).hexdigest()
    timestamp = int(time.time() * 1000)
    r = ''.join(random.choices(string.digits, k=4))

    return {
        'bduss': bduss,
        'baiduid': baiduid,
        'isid': isid,
        'rsv_pq': rsv_pq,
        'rsv_t': rsv_t,
        'rsv_sid': rsv_sid,
        'clist': clist,
        '_cr1': _cr1,
        'timestamp': timestamp,
        'r': r
    }

def clean_html_tags(html_content):
    clean_text = re.sub('<[^<]+?>|\\n', '', html_content)
    clean_text = ' '.join(clean_text.split())
    return clean_text

def convert_date_format(date_str):
    date_formats = [
        (r"(\d+)分钟前", lambda m: (datetime.now() - timedelta(minutes=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"(\d+)小时前", lambda m: (datetime.now() - timedelta(hours=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"今天", lambda m: datetime.now().strftime('%Y-%m-%d')),
        (r"昨天", lambda m: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
        (r"昨天 (\d+:\d+)", lambda m: (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')),
        (r"前天", lambda m: (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')),
        (r"前天 (\d+:\d+)", lambda m: (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')),
        (r"(\d+)天前", lambda m: (datetime.now() - timedelta(days=int(m.group(1)))).strftime('%Y-%m-%d')),
        (r"(\d+)月(\d+)日", lambda m: f"{datetime.now().strftime('%Y')}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"),
        (r"(\d+)年(\d+)月(\d+)日", lambda m: f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}")
    ]
    
    for fmt, func in date_formats:
        match = re.match(fmt, date_str)
        if match:
            return func(match)
    return date_str

# Engine metadata
about = {
    "website": "https://www.baidu.com",
    "wikidata_id": "Q3077586",
    "official_api_documentation": None,
    "use_official_api": False,
    "require_api_key": False,
    "results": "JSON",
}

# Engine configuration
paging = True
results_per_page = 20
categories = ["general"]

# Search URL
base_url = "https://www.baidu.com/s"

cookie = {
    "innersign": "0",
    "buvid3": "".join(random.choice(string.hexdigits) for _ in range(16)) + "infoc",
    "i-wanna-go-back": "-1",
    "b_ut": "7",
    "FEED_LIVE_VERSION": "V8",
    "header_theme_version": "undefined",
    "home_feed_column": "4",
}

def extract_data(html_content):
    tree = etree.HTML(html_content, parser=etree.HTMLParser(encoding="utf-8"))
    search_results = tree.xpath('//div[@tpl="se_com_default"]')
    result_data = []
    match_count = 0

    for result in search_results:
        title_element = result.xpath('.//h3[@class="c-title"]')
        
        url = result.get("mu")
        
        description = ""
        date_time = ""
        source = ""
        
        ranking = result.get("id", 0)
        
        summary_element = result.xpath('.//span[starts-with(@class, "content-right_")]')
        if summary_element:
            if summary_element[0].text:
                description = clean_html_tags(summary_element[0].text.strip())
        
        date_time_element = result.xpath('.//span[@class="c-color-gray2"]')
        if date_time_element:
            date_time = date_time_element[0].text.strip()
            date_time = convert_date_format(date_time)
        
        source_element = result.xpath('.//span[@class="c-color-gray"]')
        if source_element:
            source = source_element[0].text.strip()
        
        if title_element and url:
            title_text = clean_html_tags(title_element[0].text.strip())
            # if keyword in title_text:
                # match_count += 1
            result_data.append(
                {
                    "title": title_text,
                    "url": url,
                    "description": description,
                    "date_time": date_time,
                    "source": source,
                    "ranking": ranking,
                }
            )

    return result_data, match_count

def request(query, params):

    keyword = query.strip()

    random_params = gen_random_params()

    headers = {
            "cookie": f'BAIDUID={random_params["baiduid"]}:FG=1; BAIDUID_BFESS={random_params["baiduid"]}:FG=1; '
            f'BDUSS={random_params["bduss"]}; H_PS_645EC={random_params["rsv_t"]}; H_PS_PSSID={random_params["rsv_sid"]}',
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Connection": "close",
    }

    query_params = {
        "wd": keyword,
        "ie": "utf-8",
        "f": "8",
        "rsv_bp": "1",
        "rsv_idx": "1",
        "tn": "baidu",
        "fenlei": "256",
        "rqlang": "cn",
        "rsv_enter": "1",
        "rsv_dl": "tb",
        "rsv_btype": "i",
        "inputT": "2751",
        "mod": "1",
        "isbd": "1",
        "isid": random_params["isid"],
        "rsv_pq": random_params["rsv_pq"],
        "rsv_t": random_params["rsv_t"],
        "tfflag": "1",
        "bs": keyword,
        "rsv_sid": random_params["rsv_sid"],
        "_ss": "1",
        "clist": random_params["clist"],
        "hsug": "",
        "f4s": "1",
        "csor": "20",
        "_cr1": random_params["_cr1"],
    }

    if "site:" in keyword:
        site = keyword.split("site:")[1].strip()
        query_params["si"] = site
        query_params["ct"] = "2097152"

    if 'pageno' in params:
        query_params["pn"] = str((int(params['pageno']) - 1) * 10)

    params["url"] = f"{base_url}?{urlencode(query_params)}"
    params["headers"] = headers

    return params

def response(resp):
    html_content = resp.text

    results = []

    if "百度安全验证" in html_content or html_content.strip() == "":
        return {"code": 501, "msg": "百度PC安全验证"}
    if "未找到相关结果" in html_content:
        return {"code": 404, "msg": "未找到相关结果"}
    
    search_results, match_count = extract_data(html_content)


    return []
