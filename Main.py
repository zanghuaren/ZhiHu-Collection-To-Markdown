import requests
import re
import html2text
import time
import json


# 把问题名作为文件名，替换其中的非法字符
def rename(filename):
    illegal_characters = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_characters:
        filename = filename.replace(char, '')
    return filename


# 获取收藏夹回答数量
def get_answer_count(url, cookies, headers, params):
    resp = requests.get(url, params=params, cookies=cookies, headers=headers)
    pattern = r'"answerCount":\s*(\d+)'
    resp.close()
    return int(re.search(pattern, resp.text).group(1))


# 获取每个回答的json
def get_page_json(url, cookies, headers, params):
    response = requests.get(
        f"https://www.zhihu.com/api/v4/collections/{url.split('/')[-1]}/items",
        params=params,
        cookies=cookies,
        headers=headers,
    )
    response.close()
    return response.json()['data']


def get_answer_content(answer):
    try:
        title = rename(answer['content']['question']['title'])
        # 普通回答
    except:
        try:
            title = rename(answer['content']['title'])
            # 文章或视频
        except:
            title = '想法：' + rename(answer['content']['content'][0]['title'])
            # 想法
    # -------------------------------------------------以上获取标题，以下获取内容
    # 先获取html,再转换为markdown

    try:
        # 想法
        html_content = answer['content']['content'][0]['content']
    except:
        try:
            # 文章和回答
            html_content = answer['content']['content']
        except:
            # 视频
            html_content = '请点击作者观看视频...'

    converter = html2text.HTML2Text()
    try:
        md_text = converter.handle(html_content)
        # 回答
    except:
        md_text = converter.handle(html_content[0]['content'])
        # 文章
    return {'title': title, 'md_text': md_text, 'url': answer['content']['url'], 'autor': answer['content']['author']['name']}


def re_connect(start, end, url, params, cookies, headers):
    try:
        for offset in range(start, end, 20):
            # if offset == 60:
            #     break
            # 调试使用
            page = int(offset / 20) + 1
            offset = int(offset / 20) * 20
            params['offset'] = offset
            print(f'\n第{page}页')
            time.sleep(1)
            print('\n保护服务器，休眠1秒...\n')
            i = 1
            # 计数器，每页的第i个回答
            for answer in get_page_json(url, cookies, headers, params):
                number = i + (page - 1) * 20
                i += 1
                ord = get_answer_content(answer)
                # print(ord['autor'])
                print(str(number) + '. ' + ord['title'])
                print(ord['url'])
                head = f"> Autor: [{ord['autor']}]({ord['url']})\n\n"
                with open(str(number) + '. ' + ord['title'] + '.md', "w", encoding="utf-8") as file:
                    file.write(head)
                    file.write(ord['md_text'])
    except:
        print("已断开连接，正在重连...")
        time.sleep(5)
        return re_connect(offset, end, url, params, cookies, headers)


def main():
    with open("Cookies.json", "r", encoding="utf-8") as file:
        cookies = json.load(file)
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-requested-with': 'fetch',
        'x-zse-93': '101_3_3.0',
        'x-zse-96': '2.0_/GxPOTfBlYaCX8WCwfANfRspUUUpjeixSWqb9pFJ8k2LmAOotT5JeofvwNkM8bZb',
    }
    url = input('请输入url:')
    params = {
        'offset': '0',
        'limit': '20',
    }

    print(f'收藏夹总回答数量:{get_answer_count(url, cookies, headers, params)}')
    # for answer in get_page_json(url, cookies, headers, params):
    #     print(get_answer_content(answer)['autor'])
    #     print('--------------------')
    re_connect(0, get_answer_count(url, cookies, headers, params),
               url, params, cookies, headers)


main()
