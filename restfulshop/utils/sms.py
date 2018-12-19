import requests, json

class YunPianSMSService(object):
    """
    发送短信验证码
    """
    def __init__(self, API_KEY):
        self.API_KEY = API_KEY
        self.send_api = 'https://sms.yunpian.com/v2/sms/single_send.json'

    def send_sms(self, mobile, code):
        """
        发送验证码函数
        :param mobile: 目标手机号
        :param code: 四位验证码的值
        :return:
        """
        response = requests.post(self.send_api, data={
            'apikey': self.API_KEY,
            'mobile': mobile,
            'text': '【生鲜商城】您的验证码是{}。如非本人操作，请忽略本短信'.format(code)
        })
        data = json.loads(response.text)
        # 将短信发送的结果返回。
        return data