import requests

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from .models import User, Trip
from django.core.exceptions import ValidationError
# from django.db import IntegrityError

from braces.views import LoginRequiredMixin

from . import forms
from . import countries_info


# MapQuest API Key
key = "03cXzah4oYwdKkvyfkPeeatkbBn2z3LO"


class SignUp(CreateView):

    template_name = "accounts/signup.html"
    success_url = reverse_lazy("thanks")
    form_class = forms.UserCreateForm


class Profile(DetailView):

    model = User
    slug_field = "username"
    template_name = "accounts/profile.html"

    def get_object(self, *args, **kwargs):
        return self.request.user


class TripList(ListView):

    model = Trip
    context_object_name = "trips"
    template_name = "accounts/my_trips.html"
    paginate_by = 3

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class TripView(CreateView):

    model = Trip
    template_name = "accounts/create_trip.html"
    fields = ['country', 'town_1', 'town_2', 'fuel_cost', 'fuel_consumption']
    success_url = reverse_lazy("accounts:my_trips")

    def form_valid(self, form):
        super().form_valid(form)

        try:

            url = 'http://www.mapquestapi.com/directions/v2/optimizedroute?key=' + key + \
                  '&json={"locations":["' + self.object.town_1 + ',' + countries_info.countries[form.instance.country.lower()] + \
                  '","' + self.object.town_2 + ',' + countries_info.countries[form.instance.country.lower()] + '"]}'

            req = requests.get(url)

            json_obj = req.json()

            self.object.country = self.object.country.capitalize() 

            form.instance.distance = int(json_obj['route']['distance']*1.609344)

            fuel_used = self.object.fuel_consumption*form.instance.distance
        
            form.instance.money = int(fuel_used*self.object.fuel_cost/100)
            form.instance.time = json_obj['route']['formattedTime']
            form.instance.user = self.request.user
            
        except KeyError:
            raise ValidationError("One of the cities does not exist in our list of data!")
        else:
            return super().form_valid(form)


class TripDelete(DeleteView):

    model = Trip
    success_url = reverse_lazy('accounts:my_trips')