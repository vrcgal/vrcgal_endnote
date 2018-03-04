from django.conf.urls import url

from .views import CitationList, search, upload

app_name = 'app'
urlpatterns = [
    url(r'^$', CitationList.as_view(), name='citation-list'),
    url(r'^search/$', search, name='search'),
    url(r'^upload/$', upload, name='upload')
]
