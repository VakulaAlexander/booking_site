import django_filters
from .models import event, city, ageRestrictions, eventType


class EventFilter(django_filters.FilterSet):
    city = django_filters.ModelChoiceFilter(
        queryset=city.objects.filter(event__isnull=False).distinct().order_by('cityName'),
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
    type = django_filters.ModelChoiceFilter(
        queryset=eventType.objects.all(),
        field_name='type',
        label='Тип мероприятий',
        empty_label='Все типы'
    )

    class Meta:
        model = event
        fields = ['city', 'age', 'type']