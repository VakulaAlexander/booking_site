from django.contrib import admin
from .models import event, organisator, ageRestrictions, adress, City

# Register your models here.
admin.site.register(event)
admin.site.register(organisator)
admin.site.register(ageRestrictions)
admin.site.register(adress)
admin.site.register(City)