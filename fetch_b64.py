import urllib.request
import base64
import ssl

url = "https://tituscollege.ac.in/images/logo.png"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        b64 = base64.b64encode(response.read()).decode()
        with open("b64_logo.txt", "w") as f:
            f.write(b64)
        print("Success")
except Exception as e:
    print(e)
