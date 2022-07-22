import time

import requests
import threading
from hashlib import md5
headers = {"Accept": "application/json","Accept-Encoding": "gzip, deflate, br","Accept-Language": "zh-cn","Connection": "keep-alive","Content-Length": "379","Content-Type": "application/json","Host": "www.hulizhushou.com","If-None-Match": "3d880c0872db5d9aac67866d45c4886f","User-Agent": "%E6%8A%A4%E7%90%86%E5%8A%A9%E6%89%8B/50021 CFNetwork/1327.0.4 Darwin/21.2.0",}


call_id_g = "5310a7843a7d0f255a441af0528125d4"
acc_token = "5310a7843a7d0f255a441af0528125d4"
semaphore = threading.Semaphore(4)
def study_video(id,vid):
    semaphore.acquire()
    url = "https://www.hulizhushou.com/api/2.0/hlzs/video_study/flush_video"
    for i in range(0,110):
        data = {
            "id": id,
            "vid": vid,
            "last_et": i*60,
            "rngs": [
                {
                    "s": i*60,
                    "e": (i+1)*60
                }
            ],
            "flag": "t2",
            "sysVersion": "14.7.1",
            "deviceModel": "iPhone",
            "codeVersion": "5.3.0",
            "method": "hlzs/video_study/flush_video",
            "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
            "call_id": call_id_g,
            "apiversion": "2.0",
            "sig": "6d6f5259616e117732007967267c9c28",
            "access_token": acc_token
        }
        data["sig"] = getSigAndCallId(data["call_id"], data["method"])
        try:
            requests.post(url,json=data,headers=headers).json()
        except:
            print(f"{id}--{vid}网络堵塞，即将重新学习")
            study_video(id, vid)
    print(f"{id}--{vid}已经学习")
    semaphore.release()

def getVid(id):
    url = "https://www.hulizhushou.com/api/2.0/hlzs/video_study/detail"
    data = {
      "project_id": id,
      "sysVersion": "14.7.1",
      "deviceModel": "iPhone",
      "codeVersion": "5.3.0",
      "method": "hlzs/video_study/detail",
      "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
        "call_id": call_id_g,
      "apiversion": "2.0",
        "sig": "88a6dde6ffea93c72bc0d6c05fb70595",
        "access_token": acc_token
    }
    data["sig"] = getSigAndCallId(data["call_id"], data["method"])
    resp = requests.post(url,json=data,headers=headers).json()["data"]["video_details"]
    #print(resp)
    vid = []
    for i in resp:
        if int(i["video_total_process"])!=100:
            vid.append(i["vid"])
    return vid

def getId(itemID):
    url = "https://www.hulizhushou.com/api/1.0/hlzs/pro/plans"
    data = {
          "item_id": itemID,
          "sysVersion": "14.7.1",
          "deviceModel": "iPhone",
          "codeVersion": "5.3.0",
          "method": "hlzs/pro/plans",
          "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
          "call_id": call_id_g,
          "apiversion": "1.0",
          "sig": "",
          "access_token": acc_token
        }
    data["sig"]=getSigAndCallId(data["call_id"],data["method"])
    resp = requests.post(url, json=data, headers=headers).json()["data"]["plans"]
    id = []
    examId = []
    for i in resp:
        if "练习题" in i["title"]:
            examId.append(i["id"])
        else:
            id.append(i["id"])
    return (id,examId)

def getState(id_list):
    url = "https://www.hulizhushou.com/api/2.0/hlzs/video_study/detail"
    #id_list = getId(160699)
    data = {
        "project_id": "",
        "sysVersion": "14.7.1",
        "deviceModel": "iPhone",
        "codeVersion": "5.3.0",
        "method": "hlzs/video_study/detail",
        "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
        "call_id": call_id_g,
        "apiversion": "1.0",
        "sig": "88a6dde6ffea93c72bc0d6c05fb70595",
        "access_token": acc_token
    }
    data["sig"] = getSigAndCallId(data["call_id"], data["method"])
    for id in id_list:
        data["project_id"]=id
        resp = requests.post(url, json=data, headers=headers).json()["data"]
        msg = str(resp["project_info"]["project_name"])+"\n   完成进度-->"+str(resp["project_details"][1]["info"])+"\n   累计时长-->"+str(resp["project_details"][2]["info"])
        print(msg)



def getSigAndCallId(call_id,method):
    APIKey = "f34b59ac9857e9bbf6a7d58a5e35996b"
    APISecret = "cc52cd619a6842a679f4e8ef904824c6"
    method = method
    temp = md5()
    temp.update(("api_key=%scall_id=%smethod=%s%s"%(APIKey, call_id, method, APISecret)).encode())

    sig = str(temp.hexdigest())
    return sig




def startVideos(idd):
    id_list,examId_list = getId(idd)
    list_t = []
    for id in id_list:
        vid_list = getVid(id)
        for vid in vid_list:
            list_t.append(threading.Thread(target=study_video, args=(id, vid,)))
            # study_video(id,vid)

    for t in range(len(list_t)):
        # print("开始")
        # t.setDaemon(True)
        list_t[t].start()
    print(f"总共{len(list_t)}个视频任务，请等待")
    for t in list_t:
        t.join()
    print(f"总共{len(examId_list)}个做题任务，请等待")
    for i in examId_list:
        for _ in range(30):
            print(f"正在进行id=>{i}的第{_+1}次刷题")
            getExamAnswer(i)
    getState(id_list)

def homeStart():
    url = "https://www.hulizhushou.com/api/1.0/hlzs/pro/subjects_new"
    data = {
          "is_first": "true",
          "page": "1",
          "item_name": "",
          "sysVersion": "15.5",
          "deviceModel": "ipados",
          "codeVersion": "5.8.0",
          "method": "hlzs/pro/subjects_new",
          "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
          "_project": "hlzs",
          "call_id": call_id_g,
          "apiversion": "1.0",
          "sig": "87805f7bd861e223026be0f2dc03033f",
          "access_token": acc_token
    }
    data["sig"] = getSigAndCallId(data["call_id"], data["method"])
    resp = requests.post(url,json=data,headers=headers).json()["data"]['subjects']
    for i in resp:
        print(f"id=>{i['id']} , title=> {i['title']}")

def getExamAnswer(idd):
    url_fetch = "https://www.hulizhushou.com/api/1.0/hlzs/paper/fetch"
    data = {
        "project_id": str(idd),
        "paper_id": "v3",
        "sysVersion": "15.5",
        "deviceModel": "ipados",
        "codeVersion": "5.8.0",
        "method": "hlzs/paper/fetch",
        "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
        "_project": "hlzs",
        "call_id": call_id_g,
        "apiversion": "1.0",
        "sig": "32269778d7ea77541bc19375661c1ff8",
        "access_token": acc_token
    }
    data["sig"] = getSigAndCallId(data["call_id"], data["method"])
    resp = requests.post(url_fetch,json=data,headers=headers).json()["data"]
    temp = {}
    for i in resp["user_paper_items"]:
        temp[str(i['id'])] = {
            "sel":[str(i["qa_item"]["right_answers"])],
            "duration":"0"
        }
    result = {
        "user_paper_id":resp["user_paper_id"],
        "answer":temp,
        "sysVersion": "15.5",
        "deviceModel": "ipados",
        "codeVersion": "5.8.0",
        "method": "hlzs/paper/commit",
        "api_key": "f34b59ac9857e9bbf6a7d58a5e35996b",
        "_project": "hlzs",
        "call_id": call_id_g,
        "apiversion": "1.0",
        "sig": "bd75f847be0d13cbba3809876d914441",
        "access_token": acc_token
    }
    result["sig"] = getSigAndCallId(result["call_id"], result["method"])
    # print(resp)
    # print(result)
    url_commit = "https://www.hulizhushou.com/api/1.0/hlzs/paper/commit"
    requests.post(url_commit,json=result,headers=headers)




if __name__ == '__main__':

    homeStart()
    idd = input("请输入你要刷的课id=>")
    startVideos(idd)
    # getExamAnswer()