from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.db.models import F, Count
from django.utils import timezone

from .filters import EventFilter
from .forms import CreateUserForm, UserProfileForm, RegistrationForm, BecomeOrganizerForm, CreateEventForm, RejectEventForm
from .models import event, Registration, organisator


# Create your views here.
def is_staff(user):
    return user.is_staff

def main(request):
    return render(request, 'main/main.html')

def events(request):
    events_list = event.objects.filter(verified='approved').annotate(
        reg_count=Count('registration'),
        free_slots=F('participants') - Count('registration')
    ).order_by('event_date')

    # Применяем фильтр на основе GET-параметров
    event_filter = EventFilter(request.GET, queryset=events_list)
    filtered_events = event_filter.qs

    # Пагинация (по 6 мероприятий на страницу)
    paginator = Paginator(filtered_events, 6)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    is_organizer = False
    if request.user.is_authenticated:
        is_organizer = organisator.objects.filter(idOrganisator=request.user).exists()

    context = {
        'events': events_page,
        'filter': event_filter,
        'is_organizer': is_organizer,  # добавили
    }

    return render(request, 'main/events.html', context)


@login_required
def create_event(request):
    # Проверяем, является ли пользователь организатором
    try:
        organizer = organisator.objects.get(idOrganisator=request.user)
    except organisator.DoesNotExist:
        messages.error(request, 'Только организаторы могут создавать мероприятия.')
        return redirect('events')

    if request.method == 'POST':
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            new_event = form.save(commit=False)
            new_event.organisator = organizer
            new_event.post_date = timezone.now().date()
            new_event.verified = 'unverified'  # статус по умолчанию
            new_event.save()
            messages.success(request,
                             'Мероприятие отправлено на модерацию. После проверки оно появится в общем списке.')
            return redirect('events')
    else:
        form = CreateEventForm()

    return render(request, 'main/create_event.html', {'form': form})


def contacts(request):
    return render(request, 'main/contacts.html')

def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CreateUserForm()
    return render(request, 'main/register.html', {'form': form})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()

    return render(request, 'main/login.html', {'form': form})

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    # Проверяем, является ли пользователь организатором
    is_organizer = organisator.objects.filter(idOrganisator=request.user).exists()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    # Получаем все регистрации текущего пользователя с данными о мероприятиях
    user_registrations = Registration.objects.filter(user=request.user).select_related('event').order_by('-registration_date')

    context = {
        'form': form,
        'registrations': user_registrations,
        'is_organizer': is_organizer,
    }
    return render(request, 'main/profile.html', context)

@login_required
def become_organizer(request):
    if request.method == 'POST':
        # Проверяем, не организатор ли уже
        if organisator.objects.filter(idOrganisator=request.user).exists():
            messages.error(request, 'Вы уже являетесь организатором')
            return redirect('profile')

        form = BecomeOrganizerForm(request.POST)
        if form.is_valid():
            organisator.objects.create(
                idOrganisator=request.user,
                phone_num=form.cleaned_data['phone_num'],
                info=form.cleaned_data['info']
            )
            messages.success(request, 'Поздравляем! Вы стали организатором. Теперь вы можете создавать мероприятия.')
        else:
            # Если форма не валидна, передаём ошибки в сообщении
            errors = '; '.join([f'{field}: {", ".join(errors)}' for field, errors in form.errors.items()])
            messages.error(request, f'Ошибка: {errors}')
    return redirect('profile')

@login_required
def register_event(request, event_id):
    event_obj = get_object_or_404(event, id=event_id)

    if Registration.objects.filter(user=request.user, event=event_obj).exists():
        messages.error(request, 'Вы уже зарегистрированы на это мероприятие.')
        return redirect('events')

    with transaction.atomic():
        # Блокируем строку для избежания гонок
        event_locked = event.objects.select_for_update().get(id=event_obj.id)
        registrations_count = Registration.objects.filter(event=event_locked).count()
        free_slots = event_locked.participants - registrations_count

        if free_slots <= 0:
            messages.error(request, 'На это мероприятие больше нет свободных мест.')
            return redirect('events')

        if request.method == 'POST':
            form = RegistrationForm(request.POST, event=event_locked)
            if form.is_valid():
                Registration.objects.create(
                    user=request.user,
                    event=event_locked,
                    is_paid=(event_locked.price > 0)
                )
                messages.success(request, f'Вы успешно зарегистрированы на "{event_locked.eventName}"!')
                return redirect('events')
        else:
            form = RegistrationForm(event=event_locked)

    context = {
        'event': event_obj,
        'form': form,
        'show_card_form': event_obj.price > 0,
        'free_slots': event_obj.participants - Registration.objects.filter(event=event_obj).count(),
    }
    return render(request, 'main/register_event.html', context)

@staff_member_required
def moderation_panel(request):
    """Страница модерации для персонала: список непроверенных мероприятий"""
    unverified_events = event.objects.filter(verified='unverified').select_related(
        'organisator__idOrganisator', 'city', 'type', 'ageRestrictions'
    ).order_by('-post_date')

    context = {
        'events': unverified_events,
    }
    return render(request, 'main/moderation.html', context)


@staff_member_required
def approve_event(request, event_id):
    """Одобрить мероприятие"""
    event_obj = get_object_or_404(event, id=event_id)
    if event_obj.verified != 'unverified':
        messages.warning(request, f'Мероприятие "{event_obj.eventName}" уже обработано.')
        return redirect('moderation_panel')

    event_obj.verified = 'approved'
    event_obj.save(update_fields=['verified'])
    messages.success(request, f'Мероприятие "{event_obj.eventName}" одобрено.')
    return redirect('moderation_panel')


@staff_member_required
def reject_event(request, event_id):
    """Отклонить мероприятие с комментарием"""
    event_obj = get_object_or_404(event, id=event_id)
    if event_obj.verified != 'unverified':
        messages.warning(request, f'Мероприятие "{event_obj.eventName}" уже обработано.')
        return redirect('moderation_panel')

    if request.method == 'POST':
        form = RejectEventForm(request.POST)
        if form.is_valid():
            event_obj.verified = 'denied'
            event_obj.comment_from_admin = form.cleaned_data['comment']
            event_obj.save(update_fields=['verified', 'comment_from_admin'])
            messages.success(request, f'Мероприятие "{event_obj.eventName}" отклонено. Комментарий сохранён.')
            return redirect('moderation_panel')
    else:
        form = RejectEventForm(initial={'comment': ''})

    context = {
        'event': event_obj,
        'form': form,
    }
    return render(request, 'main/reject_event.html', context)