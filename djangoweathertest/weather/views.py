from django.shortcuts import render
import requests


def index(request):
    if request.method == "GET":
        # 如果是GET请求，说明是刷新首页。
        current_city = '郑州市'
    else:
        # 如果是POST请求，说明是form表单请求。
        current_city = request.POST.get('city')

    url = 'http://api.map.baidu.com/telematics/v3/weather?location={}&output=json&ak=TueGDhCvwI6fOrQnLM0qmXxY9N0OkOiQ&callback=?'.format(current_city)
    data = requests.get(url).json()
    weather_data = data['results'][0]['weather_data']
    return render(request, 'weather.html', {'weather_data': weather_data, 'current_city': current_city})
