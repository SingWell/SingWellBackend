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
    url(r'^choirs/(?P<pk>[0-9]+)/roster/$', views.ChoirRoster, name="Choir Roster"),
    url(r'^choirs/(?P<pk>[0-9]+)/events/$', views.EventsForChoir, name="Events for Choir"),
    ### Event endpoints
    # url(r'^organizations/(?P<org_id>[0-9]+)/events/$', views.EventList.as_view(), name="Event List"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/events/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name="Event Detail"),
    # new
    url(r'^events/$', views.EventList.as_view(), name="Event List"),
    url(r'^events/(?P<pk>[0-9]+)/$', views.EventDetail.as_view(), name="Event Detail"),
    url(r'^events/(?P<pk>[0-9]+)/program/$', views.EventProgramList.as_view(), name="Event Program"),

    ### Program endpoints
    url(r'^programFields/(?P<pk>[0-9]+)/$', views.ProgramFieldDetail.as_view(), name="Program Field Detail"),
# todo: make view for adding to a program's music

    ### Music library endpoints
    # url(r'^organizations/(?P<org_id>[0-9]+)/musicRecords/$', views.MusicRecordList.as_view(), name="Music Record List"),
    # url(r'^organizations/(?P<org_id>[0-9]+)/musicRecords/(?P<pk>[0-9]+)/$', views.MusicRecordDetail.as_view(), name="Music Record Detail"),
    url(r'^musicRecords/$', views.MusicRecordList.as_view(), name="Music Record List"),
    url(r'^musicRecords/(?P<pk>[0-9]+)/$', views.MusicRecordDetail.as_view(), name="Music Record Detail"),

    ### Music Resource endpoints
    url(r'^musicResources/$', views.MusicResourceList.as_view(), name="Music Resource List"),
    url(r'^musicResources/(?P<pk>[0-9]+)/$', views.MusicResourceDetail.as_view(), name="Music Resource Detail"),
    url(r'^resource/$', views.MusicResourceUpDown, name="Music Resource List upload download"),
    url(r'^parse/$', views.LibraryUpload, name="Library Upload and parse"),


    ### User endpoints
    url(r'^users/$', views.UserList.as_view(), name="User List"),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name="User Detail"),
    url(r'^login/$', views.UserLogin.as_view(), name='Login'),
    url(r'^register/$', views.UserCreate.as_view(), name='Register'),
    url(r'^profile/$', views.UserEdit.as_view(), name='Get User info/Edit User'),
    url(r'^profilePictures/$', views.ProfilePicture, name="Profile pic upload"),
    

    ## Choirs for a user
    url(r'users/(?P<user_id>[0-9]+)/choirs/$', views.ChoirsForUser, name="Choirs for User")
    ]

urlpatterns = format_suffix_patterns(urlpatterns)
