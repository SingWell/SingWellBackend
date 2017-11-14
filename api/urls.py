from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    ### Organization endpoints
    url(r'^organizations/$', views.OrganizationList.as_view(), name="Organization List"),
    url(r'^organizations/(?P<pk>[0-9]+)/$', views.OrganizationDetail.as_view(), name="Organization Detail"),

    ### Choir endpoints
    url(r'^organizations/(?P<org_id>[0-9]+)/choirs/$', views.ChoirList.as_view(), name="Choir List"),
    # org_id gets used as a kwarg in the filter on the view, pk is automatically used to select the proper choir
    url(r'^organizations/(?P<org_id>[0-9]+)/choirs/(?P<pk>[0-9]+)/$', views.ChoirDetail.as_view(), name="Choir Detail"),

    ### User endpoints
    url(r'^users/$', views.UserList.as_view(), name="User List"),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name="User Detail"),
    ]

urlpatterns = format_suffix_patterns(urlpatterns)
