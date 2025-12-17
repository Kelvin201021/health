from django.shortcuts import render

def landing_page(request):
    """
    Renders the project's main landing page.
    """
    return render(request, 'landing.html')
