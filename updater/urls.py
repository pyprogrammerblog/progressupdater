from django.urls import path, include
from rest_framework.routers import DefaultRouter
from updater import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'taskupdater', views.LogUpdaterModelViewSet)

app_name = 'updater'

urlpatterns = [
    path('', include(router.urls)),
]