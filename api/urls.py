from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    ### Organization endpoints
    url(r'^organizations/$', views.OrganizationList.as_view(), name="Organization List"),
    url(r'^organizations/(?P<pk>[0-9]+)/$', views.OrganizationDetail.as_view(), name="Organization Detail"),

    ### Choir endpoints
    # url(r'^organizations/(?P<org_id>[0-9]+)/choirs/$', views.ChoirList.as_view(), name="Choir List"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/choirs/(?P<pk>[0-9]+)/$', views.ChoirDetail.as_view(), name="Choir Detail"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/choirs/(?P<choir_id>[0-9]+)/roster/$', views.ChoirRoster, name="Choir Roster"),
    # new
    url(r'^choirs/$', views.ChoirList.as_view(), name="Music Record List"),
    url(r'^choirs/(?P<pk>[0-9]+)/$', views.ChoirDetail.as_view(), name="Music Record Detail"),
    url(r'^choirs/(?P<choir_id>[0-9]+)/roster/$', views.ChoirRoster, name="Choir Roster"),

    ### Event endpoints
    # url(r'^organizations/(?P<org_id>[0-9]+)/events/$', views.EventList.as_view(), name="Event List"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/events/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name="Event Detail"),
    # new
    url(r'^events/$', views.EventList.as_view(), name="Event List"),
    url(r'^events/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name="Event Detail"),

    ### Music library endpoints
    # url(r'^organizations/(?P<org_id>[0-9]+)/musicRecords/$', views.MusicRecordList.as_view(), name="Music Record List"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/musicRecords/(?P<pk>[0-9]+)/$', views.MusicRecordDetail.as_view(), name="Music Record Detail"),
    url(r'^musicRecords/$', views.MusicRecordList.as_view(), name="Music Record List"),
    url(r'^musicRecords/(?P<pk>[0-9]+)/$', views.MusicRecordDetail.as_view(), name="Music Record Detail"),

    ### User endpoints
    url(r'^users/$', views.UserList.as_view(), name="User List"),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name="User Detail"),
    url(r'^login/$', rest_framework_views.obtain_auth_token, name='Login'),
    url(r'^register/$', views.UserCreate.as_view(), name='Register'),
    url(r'^profile/$', views.UserEdit.as_view(), name='Get User info/Edit User'),

    ## Choirs for a user
    url(r'users/(?P<user_id>[0-9]+)/choirs/$', views.ChoirsForUser, name="Choirs for User")
    ]

urlpatterns = format_suffix_patterns(urlpatterns)
