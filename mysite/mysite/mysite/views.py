from django.http import Http404, HttpResponseRedirect, HttpResponseNotFound


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена!!!')
