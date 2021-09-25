from django.db import models
from django.contrib.auth import get_user_model


WEATHERUNIT_CHOICES = (
    ("IMP", "imperial"),
    ("MET", "metric"),
)


class City(models.Model):
    city = models.CharField(max_length=40, null=True)

    class Meta:
        verbose_name_plural = 'cities'
    
    def __str__(self):
        return self.city

class Default(models.Model):
    default = models.ForeignKey(
        City,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        if self.default:
            return self.default.city
        else:
            return "null"

class PersonalWeather(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    cities = models.ManyToManyField(City)
    default = models.OneToOneField(
        Default,
        on_delete=models.CASCADE,
        null=True,
    )
    unit = models.CharField(max_length=3, choices=WEATHERUNIT_CHOICES, default="MET")

    def __str__(self):
        if self.default:
            return f"{self.user}, {self.default.default}"
        else:
            return f"{self.user}, null"
