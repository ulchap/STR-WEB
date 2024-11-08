from django.contrib import admin
from django.urls import path, re_path
from car import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.MainView.as_view(), name='main'),
    path('admin/', admin.site.urls),
    path('about_company/',views.about_company),
    path('contacts/',views.contacts),

    path('news/',views.news, name='news'),
    path('article/<int:art_id>/', views.article, name='article'),

    path('promocodes/',views.promocodes),

    path('qa/',views.qa, name='qa'),
    path('qa/<int:id>/', views.detail_qa, name='detail_qa'),

    path('reviews/',views.reviews),
    path('vacancies/',views.vacancies),
    path('statistics/',views.statisticsv),
    path('service/<int:service_id>/', views.ServiceDetailView.as_view(), name='service_detail'),

    path('cart/', views.cart_detail, name='cart'),
    path('add_to_cart/<int:service_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/<int:service_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),

    path('register/master/<int:master_id>',views.mastersview, name="master"),
    path('login/master/<int:master_id>',views.mastersview, name="master"),
    path('register/client/<int:client_id>',views.clientsview, name="client"),
    path('login/client/<int:client_id>',views.clientsview, name="client"),
    path('register/',views.register),
    path('login/',views.login),

    re_path(r'^(login|register)/master/editmaster/(?P<master_id>\d+)', views.editmaster, name="editmaster"),
    re_path(r'^(login|register)/client/editclient/(?P<client_id>\d+)', views.editclient, name="editclient"),

    re_path(r'^(login|register)/client/createorder/(?P<client_id>\d+)', views.createorder, name="createorder"),

    
    re_path(r'^(login|register)/client/editreview/(?P<client_id>\d+)/(?P<review_id>\d+)', views.editreview, name="editreview"),
    re_path(r'^(login|register)/client/deletereview/(?P<client_id>\d+)/(?P<review_id>\d+)', views.deletereview, name="deletereview"),
    re_path(r'^(login|register)/client/createreview/(?P<client_id>\d+)', views.createreview, name="createreview"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)