from django.conf.urls import url, include
from . import views

app_name = 'library'

urlpatterns = [
    url(r'^$', views.index, name='index'),  # index is a function in views.py
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$',views.login,name='login'),
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^(?P<book_id>[0-9]+)/$',views.detail,name='detail'),
    url(r'^(?P<book_id>[0-9]+)/request_book/$',views.request_book,name='request_book'),
    url(r'^user_profile/$',views.user_profile,name='user_profile'),
    url(r'^renew/(?P<book_request_id>[0-9]+)/$',views.renew,name='renew')
] 