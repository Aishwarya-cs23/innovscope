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

    path('roadmap/', views.roadmap, name='roadmap'),

    path("funding/", views.funding, name="funding"),

    path(
    "legal-audit/",
    views.legal_audit,
    name="legal_audit"

    ),

    path(
    "business-model/",
    views.business_model,
    name="business_model"
    ),

]