import requests

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView, TemplateView
from .models import User, Trip, InternationalTrip
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseRedirect

from django.contrib.auth import authenticate, login

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin


from braces.views import LoginRequiredMixin

from . import forms
from . import countries_info



# MapQuest API Key
key = "03cXzah4oYwdKkvyfkPeeatkbBn2z3LO"


class SignUp(CreateView):
    '''
    SignUp view that uses the UserCreateForm that I've created.
    Logging in after registration success.
    '''

    template_name = "accounts/signup.html"
    success_url = reverse_lazy("home")
    form_class = forms.UserCreateForm

    # Login the user after Signing up
    def form_valid(self, form):
        valid = super().form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid


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
    # paginate_by = 3

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['international_trips'] = InternationalTrip.objects.filter(user=self.request.user)
        return context



class ChooseTripTypeView(TemplateView):

    template_name = "accounts/create_trip.html"



class TripView(CreateView):

    model = Trip
    template_name = "accounts/non_international.html"
    fields = ['country', 'From', 'to', 'fuel_cost', 'fuel_consumption']
    success_url = reverse_lazy("accounts:my_trips")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["non_international"] = context["form"]

        return context


    def form_valid(self, form):
        super().form_valid(form)

        try:
            url = 'http://www.mapquestapi.com/directions/v2/optimizedroute?key=' + key + \
                  '&json={"locations":["' + self.object.From + ',' + countries_info.countries[form.instance.country.lower()] + \
                  '","' + self.object.to + ',' + countries_info.countries[form.instance.country.lower()] + '"]}'

            req = requests.get(url)

            json_obj = req.json()

            self.object.country = self.object.country.capitalize()
            self.object.From = self.object.From.capitalize()
            self.object.to = self.object.to.capitalize()


            form.instance.distance = int(json_obj['route']['distance']*1.609344)

            fuel_used = self.object.fuel_consumption*form.instance.distance
        
            form.instance.money = int(fuel_used*self.object.fuel_cost/100)
            form.instance.time = json_obj['route']['formattedTime']
            form.instance.user = self.request.user
            
        except (KeyError, IntegrityError):
            form.add_error('__all__', "One of the cities does not exist in our data set!")
            return super().form_invalid(form)
        else:
            try:
                return super().form_valid(form)
            except:
                form.add_error('__all__', "You already have this trip in your MY TRIPS tab!")
                return super().form_invalid(form)



class InternationalTripView(CreateView):

    model = InternationalTrip
    template_name = "accounts/international.html"
    fields = ['first_country', 'From', 'second_country', 'to', 'fuel_cost', 'fuel_consumption']
    success_url = reverse_lazy("accounts:my_trips")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["international"] = context["form"]

        return context

    def form_valid(self, form):

        super().form_valid(form)

        try:
            url = 'http://www.mapquestapi.com/directions/v2/optimizedroute?key=' + key + \
                  '&json={"locations":["' + self.object.From + ',' + countries_info.countries[form.instance.first_country.lower()] + \
                  '","' + self.object.to + ',' + countries_info.countries[form.instance.second_country.lower()] + '"]}'

            req = requests.get(url)

            json_obj = req.json()

            # Checking whether the API statuscode signals an error.
            if json_obj['info']['statuscode'] == 402:
                form.add_error('__all__', "It is impossible to travel by a car from {} to {}".format(self.object.From.title(), self.object.to.title()))
                return super().form_invalid(form)

            self.object.first_country = self.object.first_country.capitalize()
            self.object.second_country = self.object.second_country.capitalize()
            self.object.From = self.object.From.capitalize()
            self.object.to = self.object.to.capitalize()

            form.instance.distance = int(json_obj['route']['distance']*1.609344)

            fuel_used = self.object.fuel_consumption*form.instance.distance
        
            form.instance.money = int(fuel_used*self.object.fuel_cost/100)
            form.instance.time = json_obj['route']['formattedTime']
            form.instance.user = self.request.user

            
        except (KeyError, IntegrityError):
            form.add_error('__all__', "One of the cities does not exist in our data set!")
            return super().form_invalid(form)
        else:
            try:
                return super().form_valid(form)
            except:
                form.add_error('__all__', "You already have this trip in your MY TRIPS tab!")
                return super().form_invalid(form)


class TripDelete(SuccessMessageMixin, DeleteView):

    model = Trip
    success_url = reverse_lazy('accounts:my_trips')
    success_message = 'Your trip has been deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

class InternationalTripDelete(SuccessMessageMixin, DeleteView):

    model = InternationalTrip
    success_url = reverse_lazy('accounts:my_trips')
    success_message = 'Your international trip has been deleted successfully!'

    def delete(self, request, *args, **kwargs):
        messages.warning(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)