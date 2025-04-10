import requests
import re
import html2text
import time
import json
import hashlib
import os


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

#获取文件hash值
def get_file_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

#生成文件名
def get_available_filename(base_name, content, save_path):
    counter = 0
    new_name = f"{base_name}.md"
    full_path = os.path.join(save_path, new_name)
    content_hash = get_file_hash(content)

    while True:
        if not os.path.exists(full_path):
            return full_path

        with open(full_path, 'r', encoding='utf-8') as f:
            existing_hash = get_file_hash(f.read())
            if existing_hash == content_hash:
                return None

        counter += 1
        new_name = f"{base_name}({counter}).md"
        full_path = os.path.join(save_path, new_name)


def re_connect(start, end, url, params, cookies, headers, save_path):
    try:
        for offset in range(start, end, 20):
            page = int(offset / 20) + 1
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
                print(ord['title'])
                print(ord['url'])
                head = f"> Autor: [{ord['autor']}]({ord['url']})\n\n"
                full_content = head + ord['md_text']

                filename_base = ord['title']
                available_name = get_available_filename(filename_base, full_content, save_path)

                if available_name is None:
                    print(f"文件内容相同，跳过：{filename_base}.md")
                    continue

                with open(available_name, "w", encoding="utf-8") as file:
                    file.write(full_content)
                print(f"已保存为：{os.path.basename(available_name)}")
    except:
        print("已断开连接，正在重连...")
        time.sleep(5)
        return re_connect(offset, end, url, params, cookies, headers, save_path)


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

    # 读取url.json配置
    try:
        with open("url.json", "r", encoding="utf-8") as f:
            collections = json.load(f)
    except FileNotFoundError:
        print("错误：未找到url.json配置文件")
        return
    except json.JSONDecodeError:
        print("错误：url.json格式不正确")
        return

    params = {'offset': '0', 'limit': '20'}

    for collection in collections:
        url = collection.get('url')
        save_path = collection.get('path', '')

        if not url:
            print("警告：缺少url字段，跳过该配置")
            continue

        # 创建保存目录
        try:
            os.makedirs(save_path, exist_ok=True)
            print(f"\n创建目录：{save_path}")
        except Exception as e:
            print(f"创建目录失败：{str(e)}")
            continue

        print(f"\n开始处理收藏夹：{url}")
        print(f"保存路径：{save_path}")
        total = get_answer_count(url, cookies, headers, params)
        print(f"收藏夹总回答数量: {total}")
        re_connect(0, total, url, params, cookies, headers, save_path)

    input("全部下载完成，按任意键退出...")


if __name__ == "__main__":
    main()
