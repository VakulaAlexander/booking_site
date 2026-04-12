from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .filters import EventFilter
from .forms import CreateUserForm, UserProfileForm
from .models import event


# Create your views here.
def is_staff(user):
    return user.is_staff

def main(request):
    return render(request, 'main/main.html')

def events(request):
    # Получаем все мероприятия, отсортированные по дате
    events_list = event.objects.all().order_by('event_date')

    # Применяем фильтр на основе GET-параметров
    event_filter = EventFilter(request.GET, queryset=events_list)
    filtered_events = event_filter.qs

    # Пагинация (по 6 мероприятий на страницу)
    paginator = Paginator(filtered_events, 6)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    context = {
        'events': events_page,
        'filter': event_filter,   # передаём фильтр в шаблон
    }
    return render(request, 'main/events.html', context)

def contacts(request):
    return render(request, 'main/contacts.html')

def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('login')  # предполагается, что у вас есть URL с именем 'login'
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CreateUserForm()
    return render(request, 'main/register.html', {'form': form})

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')  # или другое имя URL для главной страницы

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                # Редирект на следующую страницу (если есть) или на главную
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
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профиль успешно обновлён!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'main/profile.html', {'form': form})
