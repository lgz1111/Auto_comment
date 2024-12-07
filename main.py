import requests
from json import dumps,loads
from time import sleep,time
import random
from datetime import datetime
import os
path = os.path.dirname(__file__)
os.chdir(path)
session = requests.Session()#创建一个会话
#登录
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    'Content-Type': 'application/json'
    }
setting =loads(open(
    "data/setting.json",
    "r",
    encoding="utf-8"
    ).read())
name = setting["username"]
password = setting["password"]
url_login_captcha = "https://open-service.codemao.cn/captcha/rule/v3"
url_login = "https://api.codemao.cn/tiger/v3/web/accounts/login"
data_login = {
    "identity": name,
    "password": password,
    "pid": "65edCTyg",
    "agreement_ids": [-1]
    }
data_captcha = {
    "identity":name,
    "scene":"",
    "pid":"65edCTyg",
    "deviceId":"f2dcd063129566c5ce5971f501ee40b5",
    "timestamp":int(time())
    }

response_captcha = session.post(
    url=url_login_captcha,
    data=dumps(data_captcha),
    headers=headers
    )
#print(response_getticket.json())
headers["x-captcha-ticket"] = response_captcha.json()["ticket"]

response_login = session.post(url=url_login, data=dumps(data_login), headers=headers)

with open("data/content.txt", "r",encoding="utf-8") as f_comment:
    f_content = f_comment.read()
comment_list=f_content.split("\n")
#预处理一下该列表
comment_list = ["[自动评论] (不喜可删)"+what for what in comment_list if 1]
#print(comment_list)
#作者的id和其他白名单成员
baimingdan=[
    816081061,
    771488595,
    1814582667,
    966402533,
    1737792364,
    11770768
    ]
count = 0
if response_login.status_code == 200:#登录成功
    print('登录成功!')
    my_userid = str(response_login.json()["user_info"] ["id"])
    sleep(1)
    count=0
    while True:
        #获取原创新作列表
        url_get_list = "https://api.codemao.cn/creation-tools/v1/pc/discover/newest-work?work_origin_type=ORIGINAL_WORK&offset=0&limit=200"
        new_works_data = session.get(url=url_get_list,headers=headers).json()
        new_works_list = new_works_data["items"]

        for newwork_count in new_works_list:
            try:
                work_id = str( newwork_count ["work_id"] )
                """
                #已弃用该方法
                with open("data/like_work_list.txt","r",encoding="utf-8") as f :
                    mingdan = f.read().split("\n")
                    if work_id in mingdan:
                        print("作品id为"+work_id+"的作品在列表中，不予评论点赞")
                        continue
                """
                #查看作品本身是否已点赞
                url_work_creation_tools = "https://api.codemao.cn/creation-tools/v1/works/"+work_id#生成url
                response_work_creation_tools = session.get(url=url_work_creation_tools,headers=headers)#得到response
                is_like = response_work_creation_tools.json()["abilities"]["is_praised"]#查看是否已点赞
                #点过赞就不点了
                if is_like:
                    print("作品id为{}的作品已点赞，不予评论点赞".format(work_id))
                    continue
                work_name = str( newwork_count ["work_name"] )
                nickname  = str( newwork_count ["nickname" ] )
                user_id   = str( newwork_count ["user_id"  ] )

                what = random.choice(comment_list)
                what = what.format(("@"+nickname)) if "{}" in what else what#加上昵称处理
                data_comment = dumps({'emoji_content': "", 'content':what})
                #评论
                if int(user_id) in baimingdan:
                    print("编号为 "+work_id+' 的作者在白名单内，不予评论')
                    continue
                url_comment = 'https://api.codemao.cn/creation-tools/v1/works/'+work_id+'/comment'
                response_comment = session.post(url=url_comment, headers=headers,data=data_comment)
                status_code_comment = response_comment.status_code
                if 199 < status_code_comment < 300:
                    print("编号为 "+work_id+' 的作品评论成功')
                    count+=1
                else:
                    print("编号为 "+work_id+' 的作品评论失败,状态码'+str(status_code_comment))
                    print("详情:",response_comment.text)
                    sleep(5)
                    continue
                #点赞
                url_like="https://api.codemao.cn/nemo/v2/works/"+work_id+"/like"
                response_like = session.post(url=url_like,headers=headers)
                #print("点赞状态",response_like.status_code)
                #记录作品id到已点赞id记录文件
                open("data/like_work_list.txt","a",encoding='utf-8').write (work_id+"\n")
                record_data = {
                    "评论时间":str(datetime.now()),
                    "评论作品id":work_id,
                    "作品名":work_name,
                    "作者昵称":nickname,
                    "作者id":user_id,
                    "评论内容":what
                    }
                record_conten = dumps(record_data,ensure_ascii=False)+"\n"
                open("data/record.txt","a",encoding='utf-8').write (record_conten)
                #print(record_conten)
                sleep(13)
            except:
                print("id为"+work_id+"的作品捕获到异常")

        sleep(60)
else:
    print('登录失败，请检查账号密码')
    print(response_login.text)
print("end")
