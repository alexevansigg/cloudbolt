from django.conf.urls import url
from xui.sample_use_of_dialog import views

xui_urlpatterns = [
    url(r'^add_sample_message/(?P<server_id>\d+)/$', views.add_sample_message,
        name='add_sample_message'),
    url(r'^delete_sample_message/(?P<server_id>\d+)/message/(?P<message_id>\d+)/$',
        views.delete_sample_message, name='delete_sample_message'),
]
