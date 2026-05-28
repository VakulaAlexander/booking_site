from django.contrib import admin
from .models import event, organisator, ageRestrictions, adress, city, country, eventType, Registration

# Register your models here.
admin.site.register(event)
admin.site.register(organisator)
admin.site.register(ageRestrictions)
admin.site.register(adress)
admin.site.register(city)
admin.site.register(country)
admin.site.register(eventType)
admin.site.register(Registration)