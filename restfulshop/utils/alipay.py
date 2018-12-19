from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes

import json
from restfulshop import settings


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        ordered_items = self.ordered_data(data)
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


if __name__ == "__main__":
    # return_url = 'http://127.0.0.1:8000/?charset=utf-8&out_trade_no=2012221236665332&method=alipay.trade.page.pay.return&total_amount=110.00&sign=Rk8VyAnSEGFY4hF5fblxSYSKDKOyE%2FSlpImWkCfOfTgvEEqjdxnNE7DLlUYwH3IXP4Eq%2FgGt%2FvRCsirDvp%2BsFECS5a%2FyYA9X0ukfCX%2FPSrrO2f2NDfBsB%2FIVKWSat9rwDPYwqwj9GfT9VtkxOJq5hsnn19e2yPjLwZr3v%2BWHNsfzds2w1kHzWkJDhIZGvRkc8wX4WFxd47oag4TCVBJJ3RLzdifnkS%2Fb5r%2FPFZM1BjrzmwzebzmZwC2yJIj55xxl%2BTTD%2BW%2ByBdEPEdqMQrr6SZ2y8uwRnCqcuO0nBMBEEriHzuGGnUwzSg93v%2BsyFgT5oPMdbgDHTW7DdwPfksYcWA%3D%3D&trade_no=2018121722001459230502275247&auth_app_id=2016091100484002&version=1.0&app_id=2016091100484002&sign_type=RSA2&seller_id=2088102175095835&timestamp=2018-12-17+14%3A30%3A18'
    # o = urlparse(return_url)
    # query = parse_qs(o.query)
    # processed_query = {}
    # ali_sign = query.pop("sign")[0]


    alipay = AliPay(
        # 自己沙箱应用的APPID
        appid="2016091100484002",
        # 如果用户没有再浏览器生成的支付订单中支付，而是通过支付宝app进行了订单支付，此时需要指定一个跳转地址。
        # app_notify_url：只要用户通过支付宝支付成功，支付宝就会回调这个notify_url
        app_notify_url="http://127.0.0.1:8000/",
        app_private_key_path=settings.app_private_key_path,
        # 支付宝的公钥，验证支付宝回传消息使用，不是自己生成的应用公钥
        alipay_public_key_path=settings.alipay_public_key_path,
        debug=True,  # 默认False,
        # 如果用户是在浏览器上的支付宝订单页面进行的支付操作，支付完成之后会自动跳转到网站的指定页面return_url。如果用户没有在浏览器上支付，return_url就失效了。
        return_url="http://127.0.0.1:8000/"
        # app_notify_url和return_url，只有在支付成功的前提下，支付宝才会回调。
        # app_notify_url: 相当于是支付宝给后台发送的一个通知，告诉后台用户已经支付完成了，当后台接收到这个通知之后，必须给支付宝返回一个success结果，告诉支付宝后台已经接收到这个支付结果通知了。
        # return_url：就是一个简单的支付宝回调，支付宝只负责回调这个url地址，至于这个url地址做了什么事情，与支付宝就无关了，支付宝也不会关心这个url的返回值。
    )

    # for key, value in query.items():
    #     processed_query[key] = value[0]
    # print(alipay.verify(processed_query, ali_sign))

    url = alipay.direct_pay(
        subject="测试订单",
        out_trade_no="20122244436665332",
        total_amount=110
    )
    # 这个re_url就是支付宝提供的一个扫码支付页面的Url
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    print(re_url)