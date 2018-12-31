from django.conf import settings
from django.db import models
from django.contrib import auth
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from . import countries_info

from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from django.db import IntegrityError

usr = get_user_model()

# Imports needed for city_in_country()
import os
import csv



def city_in_country(country, check_city):
    '''
    Takes a country and a city and
    checks whether the city is in that country
    using the .csv file that is created.
    '''

    with open(os.path.join(settings.BASE_DIR, 'countries.csv'), "r") as f:
        reader = csv.DictReader(f)
        data = {}
        try:
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value.lower())
                    except KeyError:
                        data[header] = [value.lower()]
            country_list = data[country.title()]

            return True if check_city.lower() in country_list else False

        except Exception as e:
            print(type(e).__name__)



class User(auth.models.User, auth.models.PermissionsMixin):

    def __str__(self):
        return self.username



class Trip(models.Model):

    user = models.ForeignKey(usr, 
                             on_delete=models.CASCADE, 
                             related_name="trips", 
                             null=True)
    country = models.CharField(max_length=60)
    From = models.CharField(max_length=60)
    to = models.CharField(max_length=60)
    fuel_cost = models.DecimalField(decimal_places=2, 
                                    max_digits=3, 
                                    validators=[MinValueValidator(Decimal('0.01'))])
    fuel_consumption = models.PositiveIntegerField(validators=[MinValueValidator(1), 
                                                   MaxValueValidator(100)])
    date = models.DateTimeField(auto_now=True)

    # Those are the fields that get displayed as a result of the TripView
    distance = models.PositiveIntegerField(default=0, 
                                           validators=[MinValueValidator(1)])
    money = models.PositiveIntegerField(default=0, 
                                        validators=[MinValueValidator(1)])
    time = models.CharField(max_length=9)
    

    class Meta:
        
        unique_together = ('From', 'to', 'user')
        ordering = ['-date']


    def validate_unique(self, exclude=None):

        try:
            super().validate_unique()
        except Exception:
            raise ValidationError("You already have this trip in your My Trips tab!")
 

    def clean(self):

        if self.country.lower() not in countries_info.countries:
            raise ValidationError("A country with the name of {} does not exist in our data set!".format(self.country.capitalize()))
        
        if not city_in_country(self.country, self.From):
            raise ValidationError("{} does not exist/is not in {}!".format(self.From, self.country.capitalize()))
        
        if not city_in_country(self.country, self.to):
            raise ValidationError("{} does not exist/is not in {}!".format(self.to, self.country.capitalize()))
        
        if self.From == self.to:
            raise ValidationError("The towns have to be different!")


    def __str__(self):

        return self.country + "/ " + self.From + ":" + self.to


    def save_model(self, request, obj, form, change):

        obj.user = request.user
        super().save_model(request, obj, form, change)



class InternationalTrip(models.Model):

    user = models.ForeignKey(usr, 
                             on_delete=models.CASCADE, 
                             related_name="international_trips", 
                             null=True)
    first_country = models.CharField(max_length=60)
    From = models.CharField(max_length=60)
    second_country = models.CharField(max_length=60)
    to = models.CharField(max_length=60)
    fuel_cost = models.DecimalField(decimal_places=2, 
                                    max_digits=3, 
                                    validators=[MinValueValidator(Decimal('0.01'))])
    fuel_consumption = models.PositiveIntegerField(validators=[MinValueValidator(1), 
                                                   MaxValueValidator(100)])
    date = models.DateTimeField(auto_now=True)

    # Those are the fields that get displayed as a result of the TripView
    distance = models.PositiveIntegerField(default=0, 
                                           validators=[MinValueValidator(1)])
    money = models.PositiveIntegerField(default=0, 
                                        validators=[MinValueValidator(1)])
    time = models.CharField(max_length=9)
    

    class Meta:

        unique_together = ('From', 'to', 'user')
        ordering = ['-date']


    def validate_unique(self, exclude=None):

        try:
            super().validate_unique()
        except Exception:
            raise ValidationError("You already have this trip in your My Trips tab!")
 

    def clean(self):

        if self.first_country.lower() not in countries_info.countries:
            raise ValidationError("A country with the name of {} does not exist in our data set!".format(self.first_country.capitalize()))

        if self.second_country.lower() not in countries_info.countries:
            raise ValidationError("A country with the name of {} does not exist in our data set!".format(self.second_country.capitalize()))
        
        if not city_in_country(self.first_country, self.From):
            raise ValidationError("{} does not exist/is not in {}!".format(self.From, self.first_country.capitalize()))
        
        if not city_in_country(self.second_country, self.to):
            raise ValidationError("{} does not exist/is not in {}!".format(self.to, self.second_country.capitalize()))

        if self.first_country == self.second_country:
            raise ValidationError("The countries have to be different!")
        
        if self.From == self.to:
            raise ValidationError("The towns have to be different!")



    def __str__(self):

        return self.first_country + "/ " + self.From + ":" + self.second_country + "/ " + self.to



    def save_model(self, request, obj, form, change):
        
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def save(self, *args, **kwargs):
        if self.money != 0:
            super().save(self, *args, **kwargs)