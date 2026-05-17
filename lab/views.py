from django.shortcuts import render


def index(request):
    """Render the static Goshen Laboratory (Naturis) index page.

    This view intentionally does not rely on any models so the app
    remains a static, easy-to-extract component of the project.
    """
    return render(request, 'lab/index.html')
