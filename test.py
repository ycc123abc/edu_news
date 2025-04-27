import requests

url = "https://jyt.qinghai.gov.cn/xw/jydt/indexf.ashx"

payload = {'namereq': '1461,1429,1425,1422,1420,1419,1426,1407,1386,1382,1381,1378,1377'}
files=[

]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)
