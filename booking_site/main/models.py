from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ageRestrictions(models.Model):
    restriction = models.CharField(max_length = 3)

    class Meta:
        verbose_name = "Возрастное ограничение"
        verbose_name_plural = "Возрастные ограничения"

    def __str__(self):
        return self.restriction

class adress(models.Model):
    country = models.CharField(null=True,blank=True,max_length = 30)
    city = models.CharField(null=True,blank=True,max_length = 30)
    street = models.CharField(null=True,blank=True,max_length = 60)
    home = models.CharField(null=True,blank=True,max_length = 10)
    open_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.street}, {self.open_time} to {self.closing_time}"

class organisator(models.Model):
    idOrganisator = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_num = models.CharField(max_length=20)
    info = models.TextField(null=True)

    class Meta:
        verbose_name = "Организатор"
        verbose_name_plural = "Организаторы"

    def __str__(self):
        return f"{self.idOrganisator.first_name} {self.idOrganisator.last_name}"

class City(models.Model):
    cityName = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.cityName

class event(models.Model):
    eventName = models.CharField(max_length=60)
    event_date = models.DateField(verbose_name="Дата события")
    event_start = models.TimeField(null=True,blank=True)
    event_end = models.TimeField(null=True,blank=True)
    post_date = models.DateField(verbose_name="Дата публикации")
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    adress = models.ForeignKey(adress, on_delete=models.CASCADE)
    organisator = models.ForeignKey(organisator, on_delete=models.CASCADE)
    participants = models.IntegerField()
    ageRestrictions = models.ForeignKey(ageRestrictions, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to='images')
    price = models.IntegerField()

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def __str__(self):
        return self.eventName

