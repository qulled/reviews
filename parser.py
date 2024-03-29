import datetime as dt
import requests
from operator import itemgetter


def get_feedback(rootId,last_week, needed_valuation=None):
    list_answer = []
    raw_data = {"imtId": rootId, "skip": 0, "take": 30, "order": "dateDesc"}
    url = "https://public-feedbacks.wildberries.ru/api/v1/summary/full"
    response = requests.post(
        url=url, headers={"Content-Type": "application/json"}, json=raw_data
    )
    response_message = response.json()
    for items in response_message["feedbacks"]:
        # print(items)
        date = items["createdDate"][:10].replace("T", " ")
        if int(items["productValuation"]) != needed_valuation or not needed_valuation:
            if date in last_week:
                dict_answer = {}
                dict_answer["review"] = items["text"]
                dict_answer["rating"] = items["productValuation"]
                dict_answer["date"] = date
                if items['matchingSize']=='ok':
                    dict_answer["size"] = 'Соответствует размеру'
                elif items['matchingSize']=='smaller':
                    dict_answer["size"] = 'Маломерит'
                elif items['matchingSize'] == 'bigger':
                    dict_answer["size"] = 'Большемерит'
                list_answer.append(dict_answer)
        newlist = sorted(list_answer, key=itemgetter('rating'))
    return newlist


def search_rootId(imtId):
    url = (
            "https://card.wb.ru/cards/detail?spp=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-1278703,-1255563&nm="
            + str(imtId)
            + ";64245978;64245979%27"
    )
    response = requests.get(url=url)
    response_message = response.json()
    for item in response_message["data"]["products"]:
        if item["id"] == imtId:
            rootId = int(item["root"])
    return rootId

def rating_control(dict):
    rating_dict = {'five':0, 'four':0, 'three':0, 'two':0, 'one':0}
    for item in dict:
        if item['rating'] == 5:
            rating_dict['five'] += 1
        elif item['rating'] == 4:
            rating_dict['four'] += 1
        elif item['rating'] == 3:
            rating_dict['three'] += 1
        elif item['rating'] == 2:
            rating_dict['two'] += 1
        elif item['rating'] == 1:
            rating_dict['one'] += 1
    return rating_dict


def size_control(dict):
    size_dict = {'bigger': 0, 'ok': 0, 'smaller': 0}
    for item in dict:
        if item['size'] == 'Большемерит':
            size_dict['bigger'] += 1
        if item['size'] == 'Соответствует размеру':
            size_dict['ok'] += 1
        if item['size'] == 'Маломерит':
            size_dict['smaller'] += 1
    return size_dict



if __name__ == "__main__":
    last_week = [str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=1)),str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=2)),str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=3)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=4)),str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=5)),str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=6)),
                 str(dt.datetime.date(dt.datetime.now()) - dt.timedelta(days=7))]
    spisok = get_feedback(search_rootId(68877131),last_week)
    print(size_control(spisok))