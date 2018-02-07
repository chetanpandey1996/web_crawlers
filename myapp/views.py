from django.http import HttpResponse
from django.shortcuts import render
from pymongo import MongoClient
from django.http import JsonResponse

import json
client = MongoClient('localhost', 27017)



def review_view(request):
    city = request.POST.get('city_name')
    hotel = request.POST.get('hotel_name')
    i = 0
    city_data = {}
    db = client['feedback']
    collection = db[city]

    data = collection.find({'name':hotel}, {'_id':0,'name':0,'total':0,'mmt':0,'tda':0})
    for d in data:
        city_data[i] = d
        i += 1
    data = json.dumps(city_data)
    data = json.loads(data)
    return JsonResponse(data, safe=False)

def city_view(request):
    print('inside')
    city = request.POST.get('cityname')
    i=0
    city_data = {}
    db = client['feedback']
    collection = db[city]

    data = collection.find({} ,{'_id': 0,'data': 0})
    for d in data:
        city_data[i]=d
        i+=1
    data = json.dumps(city_data)
    data = json.loads(data)
    return JsonResponse(data,safe=False)

def get_cities():
    i=0
    cities={}
    db = client['feedback']
    collection = db['places']
    data = collection.find()
    for d in data:
        for city_name in d['name']:
            cities[i] = city_name
            i+=1
    return cities.values()

# Create your views here.
def index_view(request):
    if request.method == 'GET':
        all_cities = get_cities()
        return render(request,'index.html',{'acities':all_cities})

