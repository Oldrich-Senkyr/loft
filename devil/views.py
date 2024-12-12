from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def show_session_data(request):
    # Získání aktuálních session dat
    session_data = request.session.items()  # Vrátí seznam klíčů a hodnot

    # Můžete zkontrolovat session data a také vytisknout je pro debugování
    print("Current session data:", session_data)

    # Vraťte je do šablony
    return render(request, 'devil/session_display.html', {'session_data': session_data})
