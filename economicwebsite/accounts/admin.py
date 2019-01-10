from django.contrib import admin
from .models import Trip, User, InternationalTrip


admin.site.register(Trip)
admin.site.register(User)
admin.site.register(InternationalTrip)