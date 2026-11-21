from django.urls import path

from . import views

urlpatterns = [
    path("api/route/", views.route_view),
]
