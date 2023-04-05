import datetime


def year(request):
    today = int(datetime.datetime.now().year)
    return {
        'year': today,
    }
