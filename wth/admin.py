from django.contrib import admin

from .models import *

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(Default)
class DefaultAdmin(admin.ModelAdmin):
    pass


@admin.register(PersonalWeather)
class PWthAdmin(admin.ModelAdmin):
    pass