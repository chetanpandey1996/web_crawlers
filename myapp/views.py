from django.shortcuts import render
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

def get_data():
    i=0
    city_data = {}
    db = client['feedback']
    collection = db['places']

    data = collection.find()
    for d in data:
        for city_name in d['name']:
            print(city_name)
            collection = db[city_name]
            city_data[i] = collection.find()
            i+=1
    return city_data

# Create your views here.
def index_view(request):
    if request.method == 'GET':
        all_data = get_data()
        data = all_data.values()

        return render(request,'index.html',{'acities':data})

