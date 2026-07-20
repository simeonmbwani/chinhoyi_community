from django.core.exceptions import PermissionDenied

def provider_verified_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'provider' and request.user.is_verified:
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied("You must be a verified provider to access this.")
    return wrap