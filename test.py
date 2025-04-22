from DrissionPage import Chromium, ChromiumOptions
from lxml import etree
op=ChromiumOptions()
op.headless=False
ch=Chromium(op)

tab=ch.new_tab()
tab.get("https://jyt.hubei.gov.cn/bmdt/gxhptlm/cxal/")

html=tab.html
tree=etree.HTML(html)

tree=tree.xpath("//li[@class='col-md-6'][1]/div[@class='calendar']//text()")
print(tree[1].replace("\n","").replace(" ","")+"-"+tree[0].replace("\n","").replace(" ",""))
