# 导出知乎收藏夹为markdown

在当前文件夹下生成，单个回答为一个md文件。只能导出自己或者别人的收藏夹。
未来可能会考虑追加其他功能。

# 更新日志

## 2025.4.5

1.订正了作者的变量名及文件头拼写错误，autor订正为author。

2.替换了readme中的运行截图。

## 2025.4.10

1.新增批量下载收藏夹内容，读取url.json获取收藏夹链接及保存路径。

2.新增验证文件重复功能，同名同hash值文章将跳过下载。

3.修改文件命名规则。

# 使用

## 1.输入json

将自己的cookie放到"cookie.json"文件中。

打开自己任意一个收藏夹，F12，右键复制curl，然后去<https://curlconverter.com/> 转换。

注意json文件要用双引号。
示例：

```
{
  "key1":value1,
  "key2":value2
}
```

## 2.输入收藏夹url

将需要下载的收藏夹链接及保存路径放到"url.json"文件中。
示例：

```
[
    {
        "url": "https://www.zhihu.com/collection/0000001",
        "path": "D:/知乎收藏/收藏夹1"
    },
    {
        "url":"https://www.zhihu.com/collection/0000002",
        "path":""D:/知乎收藏/收藏夹2"
    }
]
```

# 运行截图

![image](https://github.com/user-attachments/assets/1443f0ec-880a-47e6-aec4-bf1d22d59dae)
