from .models import Customization

def customization(request):
    try:
        custom = Customization.objects.first()  # or .get(pk=1)
        return {'custom': custom}
    except Customization.DoesNotExist:
        return {'custom': None}