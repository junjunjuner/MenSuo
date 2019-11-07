from selenium import webdriver
from lxml import etree
from pybloomfilter import BloomFilter
import datetime
import pymongo

# 数据库连接
client = pymongo.MongoClient('10.2.46.149',1500)
db = client['ZHAOBIAO']['MenSuo']



# bloom = BloomFilter(1000000,0.001, 'caizhaowang.bloom')
bloom = BloomFilter.open('caizhaowang.bloom')

url = 'https://search.bidcenter.com.cn/search/SearchList.aspx?keywords=%E6%99%BA%E8%83%BD%E9%97%A8%E9%94%81'
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument("window-size=1024,768")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome('/home/260199/chrome/chromedriver',options=options)
driver.get(url)

source = driver.page_source
# print(source)
html = etree.HTML(source)
trs = html.xpath(".//div[@class='list_kk']/table[@id='jq_project_list']/tbody/tr")
print(len(trs[: -1]))
# 时间
now_time = datetime.datetime.now().strftime('%Y-%m-%d')

for tr in trs[: -1]:
    link = tr.xpath(".//td[@class='zb_title']/a/@href")[0].strip('/')
    # print(link)
    title = tr.xpath(".//td[@class='zb_title']/a")
    title = title[0].xpath('string(.)')
    title = title.replace('\n','').replace('\r','').strip(' ')
    print(link, title)
    key_word = tr.xpath(".//td[@class='zb_title']/font[@class='ck_xggjc']")
    if (key_word):
        key_word = key_word[0].xpath('string(.)')
    else:
        key_word = '标题包含:智能门锁'
    key_word = key_word.replace('\n','').replace('\r','').strip(' ')
    # print(key_word)
    b_type = tr.xpath(".//td[3]/text()")[0]
    # b_type = b_type[0].xpath('string(.)')
    b_type = b_type.replace('\n','').replace('\r','').strip(' ')
    # print(b_type)
    area = tr.xpath(".//td[@class='list_area']/a/text()")[0]
    area = area.replace('\n','').replace('\r','').strip(' ')
    # print(area)
    b_time = tr.xpath(".//td[@class='list_time']/text()")[0]
    b_time = b_time.replace('\n','').replace('\r','').strip(' ')
    # print(b_time)
    if title not in bloom:
        db_dict = {
            '数据来源': '采招网',
            '备注': key_word,
            '爬取时间': now_time,
            '地区': area,
            '时间': b_time,
            '类别': b_type,
            '链接': link,
            '标题': title
        }
        db.insert(db_dict)
        bloom.add(title)
    else:
        print('已保存过:', title)

client.close()

