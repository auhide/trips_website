from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('profile/<slug:slug>/', views.Profile.as_view(), name='profile'),
    path('my_trips/', views.TripList.as_view(), name='my_trips'),
    path('create_trip/', views.ChooseTripTypeView.as_view(), name='create_trip'),
    path('non_international/', views.TripView.as_view(), name='non_international'),
    path('international/', views.InternationalTripView.as_view(), name='international'),
    re_path(r'^delete_trip/(?P<pk>[0-9]+)$', views.TripDelete.as_view(), name='delete_trip'),
    re_path(r'^delete_inttrip/(?P<pk>[0-9]+)$', views.InternationalTripDelete.as_view(), name='delete_inttrip'),
]