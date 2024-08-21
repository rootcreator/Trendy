from django.urls import path
from . import views
from .views import set_region
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_view, name='search_view'),
    path('set_region/', set_region, name='set_region'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),  # Add this line
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),  # Add this line

    path('bookmark_trend/', views.bookmark_trend, name='bookmark_trend'),
    path('get-bookmarks/', views.get_bookmarks, name='get_bookmarks'),

    path('fetch-finance-data/', views.fetch_finance_data, name='fetch_finance_data'),
]
