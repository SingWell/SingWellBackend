from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^organizations/$', views.OrganizationList.as_view(), name="Organization List"),
    url(r'^organizations/(?P<pk>[0-9]+)/$', views.OrganizationDetail.as_view(), name="Single Organization Detail"),
    ]

urlpatterns = format_suffix_patterns(urlpatterns)
