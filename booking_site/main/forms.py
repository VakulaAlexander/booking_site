from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Registration, organisator, event

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }

class RegistrationForm(forms.ModelForm):
    card_number = forms.CharField(
        max_length=16,
        label='Номер карты',
        widget=forms.TextInput(attrs={'placeholder': '1111 2222 3333 4444'}),
        required=False
    )
    card_expiry = forms.CharField(
        max_length=5,
        label='Срок действия (ММ/ГГ)',
        widget=forms.TextInput(attrs={'placeholder': '12/26'}),
        required=False
    )
    card_cvv = forms.CharField(
        max_length=3,
        label='CVV',
        widget=forms.PasswordInput(attrs={'placeholder': '123'}),
        required=False
    )

    class Meta:
        model = Registration
        fields = []

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)
        if self.event and self.event.price > 0:
            # Для платных мероприятий делаем поля карты обязательными
            self.fields['card_number'].required = True
            self.fields['card_expiry'].required = True
            self.fields['card_cvv'].required = True

    def clean(self):
        cleaned_data = super().clean()
        if self.event and self.event.price > 0:
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvv = cleaned_data.get('card_cvv')
            if not (card_number and card_expiry and card_cvv):
                raise forms.ValidationError("Заполните все реквизиты карты")
            if len(card_number) != 16 or not card_number.isdigit():
                self.add_error('card_number', 'Номер карты должен содержать 16 цифр')
            if len(card_cvv) != 3 or not card_cvv.isdigit():
                self.add_error('card_cvv', 'CVV должен содержать 3 цифры')
        return cleaned_data

class BecomeOrganizerForm(forms.ModelForm):
    class Meta:
        model = organisator
        fields = ['phone_num', 'info']
        labels = {
            'phone_num': 'Контактный телефон',
            'info': 'Информация об организаторе (будет видна другим пользователям)',
        }
        widgets = {
            'phone_num': forms.TextInput(attrs={'placeholder': '+7 (xxx) xxx-xx-xx'}),
            'info': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе как об организаторе...'}),
        }

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = event
        fields = [
            'eventName', 'type', 'event_date', 'event_start', 'event_end',
            'city', 'adress', 'participants', 'ageRestrictions',
            'image', 'price', 'info', 'document', 'сomment_for_admin'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'event_start': forms.TimeInput(attrs={'type': 'time'}),
            'event_end': forms.TimeInput(attrs={'type': 'time'}),
            'info': forms.Textarea(attrs={'rows': 4}),
            'сomment_for_admin': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'eventName': 'Название мероприятия',
            'type': 'Тип мероприятия',
            'event_date': 'Дата проведения',
            'event_start': 'Время начала',
            'event_end': 'Время окончания',
            'city': 'Город',
            'adress': 'Адрес',
            'participants': 'Количество участников',
            'ageRestrictions': 'Возрастное ограничение',
            'image': 'Изображение',
            'price': 'Цена (в рублях)',
            'info': 'Описание',
            'document': 'Документы (при необходимости)',
            'сomment_for_admin': 'Комментарий для администратора'
        }

class RejectEventForm(forms.Form):
    comment = forms.CharField(
        label='Причина отклонения',
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Укажите, почему мероприятие не прошло модерацию...'}),
        required=True,
        max_length=500
    )