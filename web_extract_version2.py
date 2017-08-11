#encoding=utf8

import requests
import re
import htmlparser

'''
不知道怎么遍历DOM树，然后自己再建立出正确的DOM树
没法根据文本对象确定当前的标签是什么
所以当前的构思是，先去掉所有可能的噪音，如：重复的title、多余的表示时间的文本（影响确认新闻的发布时间），
然后认为正文是在某个div标签下面，将时间和正文放在一个文本块里
最后在唯一的文本块里找出时间和来源
至于作者，考虑的是全文正则出来：“作者：.*”
'''

def get_source(url):
    '''
    下载源码并重新编码
    '''
    resp = requests.get(url)
    encoding = resp.apparent_encoding
    if 'gb' in encoding.lower():
        encoding = 'gbk'
    print 'my encoding: ', encoding
    resp.encoding = encoding

    return resp

def denoising(resp):
    '''
    去噪
    '''
    body = re.search('(<body>[\s\S]*?</body>)', resp.text) # 只要body里的内容，因为有的title内容就存在于meta中，但是meta一般都存在于head里，body标签之外
    if body:
        unicode_html_boidy = body.group(1)
    else:
        print 'no body!!!'
        unicode_html_boidy = resp.text
    re_note = '<!--.*?-->'
    re_script = '<script.*?>([\s\S]*?)</script>'
    re_style = '<style.*?>([\s\S]*?)</style>'
    re_link = '<link.*?/*>'
    re_meta = '<meta.*?/*>'     # 因为有的title内容就存在于meta中
    re_title = '<title>([\s\S]*?)</title>'
    re_blank = '\s+'

    body = re.sub(re_note, '', unicode_html_boidy)
    body = re.sub(re_script, '', body)
    body = re.sub(re_style, '', body)
    body = re.sub(re_link, '', body)
    body = re.sub(re_meta, '', body)
    body = re.sub(re_title, '', body)
    body = re.sub(re_blank, ' ', body)

    return body

def find_text(resp):
    data = htmlparser.Parser(resp)
    titles = data.xpathall("//div|//table")     # 认为正文及时间等信息在div标签下

    div_list = []                   # 存放过滤之后的div标签
    for item in titles:
        text = item.text().strip()
        if len(text) < 12:          # 过滤没有文本对象的标签
            continue
        text = text.replace('年', '-').replace('月', '-').replace('日', ' ').replace('时', ':').replace('分', '')
        # print '1111111111', text
        if re.search('(\d+:\d+)', text):                # 认为发布时间和正文在同一个文本块里（在同一个div里），发布时间精确到分钟
            div_list.append(item)
            # print '############', text
        if re.search('(\d+[-/]\d+[-/]\d+)', text):      # 认为发布时间和正文在同一个文本块里（在同一个div里），发布时间只精确到年月日
            div_list.append(item)
            # print '############', text
    print 'all: ', len(titles)
    print 'userful: ', len(div_list)

    length = 0
    t = ''
    for item in div_list:       # 取出最长的一段文本，且认为时间和正文都在这个文本块里
        text_length = len(item.text().strip())
        if text_length > length:
            length = text_length
            t = item.text().strip()

    t_lis = t.split()           # 将最长的这段文本块进行分割，因为里面依然存在噪音信息
    # 过滤条件还是不对！！！！！！这样容易把来源过滤掉，例如：http://news.163.com/16/1226/09/C971037U000187V5.html的来源就被过滤掉了
    for item in t_lis:
        # print '############', item
        text = item.replace('年', '-').replace('月', '-').replace('日', ' ').replace('时', ':').replace('分', '')
        # print '222222222', text
        if re.search('(\d+:\d+)', text):
            continue
        if re.search('(\d+[-/]\d+[-/]\d+)', text):
            continue
        if '，' in text:
            continue
        else:
            t_lis.remove(item)
    news_text = ' '.join(t_lis)
    print 'content: ', news_text
    return news_text

def find_time(text):
    text_new = text.replace('年', '-').replace('月', '-').replace('日', ' ').replace('时', ':').replace('分', '')
    news_time = re.search('(\d+[-/]\d+[-/]\d+\s*\d*:?\d*:?\d*)', text_new)
    if news_time:
        news_time = news_time.group(1)
    else:
        print 'There is no tiem data!!!'
        news_time = 'error'

    return news_time

def main(url):
    resp = get_source(url)
    unicode_html_boidy = denoising(resp)
    news_text = find_text(unicode_html_boidy)
    news_time = find_time(news_text)
    print news_time

if __name__ == '__main__':
    url = 'http://news.sina.com.cn/china/xlxw/2016-12-25/doc-ifxyxusa5335751.shtml'
    url = 'http://news.163.com/16/1226/09/C971037U000187V5.html'
    url = 'http://health.dahe.cn/yuqing/201612/t20161226_677215.html'
    url = 'http://edu.anhuinews.com/system/2013/08/26/006023089.shtml'
    url = 'http://news.cmt.com.cn/detail/1276630.html'
    print 'url: ', url
    main(url)

