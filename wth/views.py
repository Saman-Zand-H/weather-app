from django.shortcuts import redirect, render
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from datetime import datetime

from .handlers import *
from .models import City, PersonalWeather, Default
from . import forms


class HomeView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = forms.FindCityForm(self.request.POST)

        if form.is_valid():
            location = form.cleaned_data.get("location")
            city_field, created = City.objects.get_or_create(city=location.upper())
            pwth_qs = PersonalWeather.objects.filter(user=self.request.user)

            if pwth_qs.exists():
                user_pwth = pwth_qs[0]
                location_existance = check_location_exstiance(location)
                # API response status code
                status_code = location_existance.get("cod")
                user_city_qs = user_pwth.cities.filter(city=location)

                if user_city_qs.exists():
                    messages.warning(
                        self.request, "Repetitive locations are not allowed")
                    return redirect("wth:home")
                else:
                    if status_code == "404":
                        city_field.delete()
                        messages.error(
                            self.request, "We do not have any record for this location")
                        return redirect("wth:home")
                    else:
                        default = Default.objects.filter(
                            personalweather=user_pwth)
                        new_default = default.update(default=city_field)[0]
                        user_pwth.cities.add(city_field)
                        user_pwth.default = new_default
                        user_pwth.save()
                        messages.success(
                            self.request, "Location added successfully")
                        return redirect("wth:home")
            else:
                location_existance = check_location_exstiance(location)
                status_code = location_existance.get("cod")

                if status_code == "404":
                    city_field.delete()
                    messages.error(
                        self.request, "We do not have any record for this location")
                    return redirect("wth:home")
                else:
                    default = Default.objects.create(default=city_field)
                    userwth = PersonalWeather.objects.create(
                        user=self.request.user, default=default)
                    userwth.cities.add(city_field)
                    userwth.save()
                    messages.success(
                        self.request, "Location added successfully")
                    return redirect("wth:home")

    def get(self, *args, **kwargs):
        pwth_qs = PersonalWeather.objects.filter(user=self.request.user)

        if pwth_qs.exists() and pwth_qs[0].default:
            user_pwth = pwth_qs[0]

            cities = user_pwth.cities.all()
            cities_count = user_pwth.cities.aggregate(count=Count("city"))["count"]

            location = user_pwth.default.default.city

            geocode_resp = geocode_forward_api_req(location)[0]

            lon = geocode_resp.get("lon")
            lat = geocode_resp.get("lat")

            unit = user_pwth.get_unit_display()

            date = datetime.now()

            response = wth_api_req(lon, lat, unit)

            daily_context = get_daily_weather(response)
            hourly_context = get_hourly_weather(response)
            current_wth = get_current_weather(response, location)
            current_context = {"current": current_wth}
            extra_context = {"date": date} | {"unit": unit} | {"cities": cities} | {"c_count": cities_count}
            context = daily_context | hourly_context | current_context | extra_context

            return render(self.request, "wth/home.html", context)
        else:
            geocode_resp = geocode_forward_api_req('Washington')[0]

            lon = geocode_resp.get("lon")
            lat = geocode_resp.get("lat")

            unit = "metric"

            date = datetime.now()

            response = wth_api_req(lon, lat, unit)


            daily_context = get_daily_weather(response)
            hourly_context = get_hourly_weather(response)
            current_wth = get_current_weather(response, "Washington")
            current_context = {"current": current_wth}
            extra_context = {"date": date} | {"unit": unit}
            context = daily_context | hourly_context | current_context | extra_context

            return render(self.request, "wth/home.html", context)
homeview = HomeView.as_view()


class ContactView(View):
    def post(self, *args, **kwargs):
        form = forms.ContactForm(self.request.POST)
        if form.is_valid():
            name = form.cleaned_data.get("name")
            message = form.cleaned_data.get("message")
            send_contact_email(name, message)
            messages.success(self.request, "You message sent successfully")
            return redirect("wth:home")
    def get(self, *args, **kwargs):
        return render(self.request, "wth/contact.html")

contactview = ContactView.as_view()

def unitview(request):

    if request.method == "POST":
        form = forms.UnitForm(request.POST)
       
        if form.is_valid():
            unit = form.cleaned_data.get("unit")
            set_unit(request, unit)
            messages.success(request, "Preferred unit updated")
            return redirect("wth:home")


def defaultcityview(request):

    if request.method == "POST":
        form = forms.CitiesForm(request.POST)

        if form.is_valid():
            city = form.cleaned_data.get("default_city")
            set_default_city(request, city)
            messages.success(request, "Your default location updated successfully")
            return redirect("wth:home")

def removecityview(request):

    if request.method == "POST":
        form = forms.RemoveCityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data.get("city")
            city_field = City.objects.get(city=city)
            pwth_qs = PersonalWeather.objects.filter(user=request.user)
            user_pwth = PersonalWeather.objects.get(user=request.user)
            default_qs = Default.objects.filter(personalweather=user_pwth)
            city_qs = City.objects.filter(personalweather=user_pwth)
            default = default_qs[0]
            cities = user_pwth.cities

            # User can remove a city iff they have more than one
            if cities.aggregate(count=Count("city"))["count"] > 1:
                # If the current default is the city to remove, change the default
                if default == city_field:
                    # If the city is the last, set the last but one city to default
                    if city_field == city_qs.last():
                        new_default = city_qs.reverse()[1]
                        updated_default = default_qs.update(default=new_default)
                    # Else set the last created city to default
                    else:
                        new_default = city_qs.last()
                        updated_default = default_qs.update(default=new_default)
                    user_pwth.default = updated_default
                    user_pwth.save()
                cities.remove(city_field)
                city_field.delete()
                messages.success(request, "City removed successfully")
            else:
                messages.warning(request, "In order to remove cities you need to have more than one")
                
            return redirect("wth:home")

