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


class city(models.Model):
    cityName = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self):
        return self.cityName

class country(models.Model):
    countryName = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
        return self.countryName

class adress(models.Model):
    country = models.ForeignKey(country,null=True,blank=True, on_delete=models.CASCADE)
    city = models.ForeignKey(city,null=True,blank=True, on_delete=models.CASCADE)
    street = models.CharField(null=True,blank=True,max_length = 60)
    home = models.CharField(null=True,blank=True,max_length = 10)
    open_time = models.TimeField()
    closing_time = models.TimeField()

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def __str__(self):
        return f"{self.street}, {self.home}"

class organisator(models.Model):
    idOrganisator = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_num = models.CharField(max_length=20)
    info = models.TextField(null=True) # Информация, которую видят другие пользователи об организаторе

    class Meta:
        verbose_name = "Организатор"
        verbose_name_plural = "Организаторы"

    def __str__(self):
        return f"{self.idOrganisator.first_name} {self.idOrganisator.last_name}"

class eventType(models.Model):
    type = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Тип мероприятия"
        verbose_name_plural = "Типы мероприятий"

    def __str__(self):
        return self.type


class event(models.Model):

    VERIFICATION_STATUS = [
        ('unverified', 'На проверке'),
        ('approved', 'Одобрено'),
        ('denied', 'Отказано'),
    ]

    eventName = models.CharField(max_length=60)
    type = models.ForeignKey(eventType, on_delete=models.CASCADE)
    event_date = models.DateField(verbose_name="Дата события")
    event_start = models.TimeField(null=True,blank=True)
    event_end = models.TimeField(null=True,blank=True)
    post_date = models.DateField(verbose_name="Дата публикации")
    city = models.ForeignKey(city, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Город")
    adress = models.ForeignKey(adress, on_delete=models.CASCADE)
    organisator = models.ForeignKey(organisator, on_delete=models.CASCADE)
    participants = models.IntegerField()
    ageRestrictions = models.ForeignKey(ageRestrictions, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to='images')
    price = models.IntegerField()
    info = models.TextField(null=True,blank=True, max_length=500)
    verified = models.CharField(max_length=20,choices=VERIFICATION_STATUS,
                                default='unverified',verbose_name="Статус верификации")
    document = models.FileField(upload_to='event_documents/',null=True,
                                blank=True, verbose_name="Документы"
    )
    сomment_for_admin = models.TextField(null=True, blank=True)
    comment_from_admin = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"

    def free_slots(self):
        """Возвращает количество свободных мест"""
        return self.participants - self.registration_set.count()

    def __str__(self):
        return self.eventName


class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    event = models.ForeignKey(event, on_delete=models.CASCADE, verbose_name="Мероприятие")
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")
    is_paid = models.BooleanField(default=False, verbose_name="Оплачено")

    class Meta:
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.eventName}"