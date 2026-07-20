from django.core.exceptions import PermissionDenied

def provider_verified_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # We no longer use .profile because fields are directly on request.user
        # We check the role and verification status directly
        if request.user.role == 'provider' and not request.user.is_verified:
            raise PermissionDenied("Your account is pending admin verification.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view