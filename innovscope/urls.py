from django.contrib import admin
from django.urls import path

from predictor import views

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', views.home),
    path('predict/', views.predict),

    path('register/', views.register_user),
    path('login/', views.login_user),
    path('logout/', views.logout_user),

    path('dashboard/', views.dashboard),
    path('history/', views.history),

]