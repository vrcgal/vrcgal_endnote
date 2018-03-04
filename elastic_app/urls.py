from django.conf.urls import url

from .views import CitationList, SearchList, UploadView

app_name = 'citations'
urlpatterns = [
    url(r'^$', CitationList.as_view(), name='citation-list'),
    url(r'^search/$', SearchList.as_view(), name='search'),
    url(r'^upload/$', UploadView.as_view(), name='upload')
]
