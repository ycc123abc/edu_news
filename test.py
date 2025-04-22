from DrissionPage import Chromium, ChromiumOptions
from lxml import etree
op=ChromiumOptions()
op.headless=False
ch=Chromium(op)

tab=ch.new_tab()

tab.get("https://jyt.nmg.gov.cn/zfxxgk/fdzdgknr/bmwj/index_1.html")
tab.change_mode()
html=tab.html
html.encode("utf-8")
print(html)
