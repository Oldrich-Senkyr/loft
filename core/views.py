
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.utils import translation
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Changes for forms
from .forms import SignupForm 


def index(request):
    return render(request, 'core/index.html')   #Kde lezi soubor


def switch_language(request, language_code):
    # Aktivace zvoleného jazyka
    translation.activate(language_code)
    response = redirect('core:index')  # Presmerování na domovskou stránku

    # Uložení vybraného jazyka do cookies
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language_code)


    referer = request.META.get('HTTP_REFERER')

    return response


def swl(request):
    # Získání aktuálního jazyka z URL
    current_language = translation.get_language()

    # Překlady pro různé jazyky
    messages = {
        'en': 'Welcome to our multilingual site!',
        'cs': 'Vítejte na našich vícejazyčných stránkách!',
        'de': 'Willkommen auf unserer mehrsprachigen Seite!',
    }

    # Kontext pro šablonu
    context = {
        'welcome_message': messages.get(current_language, messages['en']),  # Výchozí jazyk je angličtina
    }

    return render(request, 'core/index.html', context)

def my_logout (request):                        #Kdybych pouzil logout kolidovalo by to s internim logout
    if request.method == 'POST':
        logout(request)
        return redirect('/')
    return render(request, 'core/logout.html', {})

# Changes for forms
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('/login/')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {
        'form': form    
    })
