from django.urls import path
from . import views

urlpatterns = [
    path(route='',view=views.home_page,name='home_page')
]