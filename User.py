import os
import requests
import time
import logging
import uuid
import typing
from json import dumps
import concurrent.futures#线程池

"""
编程猫用户行为封装
"""
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Content-Type': 'application/json'
    }
class User():
    def __init__(self):
        # super().__init__()
        self.session = requests.Session()
        self.is_login = False

    def is_signatue(self):
        """根据用户等级判断是否已签订用户友好协议"""
        if not (self.is_login):
            raise ("用户未登录")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Content-Type': 'application/json'
            }
        url_check = "https://api.codemao.cn/web/users/details"
        usr_has_signed = self.session.get(url=url_check, headers=headers).json().get("has_signed")
        if usr_has_signed:
            return True
        return False

    def signature(self) ->requests.Response:
        """签订友好协议"""
        if not(self.is_login):
            raise ("用户未登录")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Content-Type': 'application/json'
            }
        url_signature = "https://api.codemao.cn/nemo/v3/user/level/signature"
        response_signature = self.session.post(url = url_signature, headers = headers, data= dumps({}) )
        if 199 < response_signature.status_code < 300:
            print(f"用户{self.username} 签订友好协议成功")
        else:
            logging.error(f"用户{self.username} 尝试签订友好协议时失败")
        return response_signature

    def login(self,username, password, pid = "65edCTyg", autosign= True) -> requests.Response:
        """登录,返回登录请求的结果"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Content-Type': 'application/json'
            }
        # 拿到ticket
        url_get_ticket = "https://open-service.codemao.cn/captcha/rule/v3"
        deviceId = uuid.uuid4().hex
        time_now = int(time.time())
        data_get_ticket = {
            "identity":str(username),
            "scene":"",
            "pid": pid,
            "deviceId":str(deviceId),
            "timestamp":time_now
            }
        response_get_ticket = self.session.post(url=url_get_ticket,headers=headers,data=dumps(data_get_ticket))
        if response_get_ticket.status_code != 200:
            logging.error(f"{username} 获取ticket失败.错误代码 {response_get_ticket.status_code}")
        else:
            # logging.info(f"{username}获取ticket成功")
            # 导入ticket
            ticket = response_get_ticket.json()["ticket"]
            headers["x-captcha-ticket"] = ticket
            headers["pid"] = pid
            # 开始登录
            url_login = "https://api.codemao.cn/tiger/v3/web/accounts/login/security"
            data_login = {
                "identity":str(username),
                "password":str(password),
                "pid":pid,
                "agreement_ids":[-1]
                }
            response_login = self.session.post(url=url_login,headers=headers,data=dumps(data_login))
            if response_login.status_code != 200:
                logging.error(f"{username} 登录失败.错误代码 {response_login.status_code}")

            else:
                print(f"{username}登录成功")
                self.is_login = True
                self.username = username
                # self.signature()
                if autosign:
                    if not(self.is_signatue()):
                        self.signature()

        return response_login
    
class WorkPageUser(User):
    """封装用户对公开作品的操作"""
    def jubao_work(self, work_id, report_reason = "抄袭", report_describe = "抄袭作品") ->requests.Response:
        """举报一个作品,work_id是作品的id"""
        if not (self.is_login):
            raise("用户未登录")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Content-Type': 'application/json'
            }
        url_jubao = "https://api.codemao.cn/nemo/v2/report/work"
        data_jubao = {"work_id":int(work_id),"report_reason":report_reason,"report_describe":report_describe}
        response_jubao = self.session.post(url=url_jubao,headers=headers,data=dumps(data_jubao))
        print(response_jubao.status_code)
        return response_jubao

    def work_like(self,work_id) ->requests.Response:
        """点赞一个作品"""
        url_like = f"https://api.codemao.cn/nemo/v2/works/{work_id}/like" # .format(workid)
        # url_p = "https://collection.codemao.cn/report/community"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
            'Content-Type': 'application/json'
            }
        # self.sesson.post(
        #     url=url_p,
            # data={
            #     "alg":"","type":0,"data":{"m":{"d":1,"p":"community","tst":False,"h":False},"e":{"resolution":"1707x960","ua":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36","platform":"win64","net":"4g","cpu":12,"density":1.5,"process_id":"995854af-0efe-49d8-94c4-0ab306436b13","uid":"68bb0945-c403-4391-b7b1-d4586be5b056","la":"zh-CN"},"b":[{"t":1738576705,"i":"e85617e7-a04a-4cd4-b3f2-bd5d380124af","e":"page_view_end","d":{"user_id":816081061,"dur":11,"url":"https://shequ.codemao.cn/work/230836484"}},{"t":1738576705,"i":"21e15fdb-4b98-4704-adee-fc149b52963f","e":"page_view_end","d":{"user_id":816081061,"dur":11,"url":"https://shequ.codemao.cn/work/230836484"}},{"t":1738576706,"i":"0b2bf50b-0d21-47b0-b876-ade59fae2417","e":"EVENT_PAGE","d":{"path":"/work/230836484","domain":"shequ.codemao.cn"}},{"t":1738576706,"i":"64eb4e60-e38e-474e-8a28-2a04c509aedf","e":"product_visit","d":{"user_id":"816081061","product_id":"230836484","visit_from":"https://shequ.codemao.cn/discover"}}]}},
            #     headers=headers)
        response_like = self.session.post(url=url_like,headers=headers)
        return response_like

    def view_work(self, work_id: str) -> requests.Response:
        response = self. session. get(f"https://api.codemao.cn/creation-tools/v1/works/{work_id}")
        return response
    
    def work_comment(self,work_id, content):
        url_comment = f'https://api.codemao.cn/creation-tools/v1/works/{work_id}/comment'
        data_comment = dumps({'emoji_content': "", 'content':content})
        response_comment = self.session.post(url=url_comment, headers=headers,data=data_comment)
        return response_comment
    
    def work_has_liked(self,work_id)->bool:
        """检查作品是否被用户点赞过。如果点赞过，返回True，否则返回False"""
        url = f"https://api.codemao.cn/creation-tools/v1/works/{work_id}"
        response_work_creation_tools = self.session.get(url=url,headers=headers)#得到response
        if response_work_creation_tools.status_code != 200 :
            raise (f"作品id为{work_id}的作品检查是否已点赞时出错，状态码{response_work_creation_tools.status_code}")
        abilities = response_work_creation_tools.json().get("abilities")
        if abilities:
            is_like = abilities.get("is_praised")#查看是否已点赞
        else:
            raise (f"作品id为{work_id}的作品检查是否已点赞时出错，返回值内容不对")
        return is_like