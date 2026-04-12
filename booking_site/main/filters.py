import django_filters
from .models import event, City, ageRestrictions

class EventFilter(django_filters.FilterSet):
    city = django_filters.ModelChoiceFilter(
        queryset=City.objects.filter(event__isnull=False).distinct().order_by('cityName'),
        field_name='city',
        label='Город',
        empty_label='Все города'
    )
    age = django_filters.ModelChoiceFilter(
        queryset=ageRestrictions.objects.all(),
        field_name='ageRestrictions',
        label='Возрастное ограничение',
        empty_label='Все категории'
    )

    class Meta:
        model = event
        fields = ['city', 'age']