from django.conf.urls import url
from xui.aws_elastic_ips import views

xui_urlpatterns = [
    url(r'^aws_elastic_ips/(?P<env>\d+)/$', views.aws_elastic_ips,name='aws_elastic_ips'),
    url(r'^aws_add_elastic_ip/(?P<env_id>\d+)/$', views.aws_add_elastic_ip,name='aws_add_elastic_ip'),
    url(r'^aws_release_elastic_ip/(?P<env_id>\d+)/(?P<allocation_id>[-A-Za-z0-9_]+)/$', views.aws_release_elastic_ip,name='aws_release_elastic_ip'),
    url(r'^aws_release_all_elastic_ip/(?P<env_id>\d+)/$', views.aws_release_all_elastic_ip,name='aws_release_all_elastic_ip'),
]
