from DrissionPage import ChromiumOptions,Chromium

co=Chromium()
tab=co.new_tab()

tab.change_mode()
tab.get("https://jw.cq.gov.cn/zwxx_209/jdtp/index.html")
html=tab.html
print(html)
tab.change_mode()