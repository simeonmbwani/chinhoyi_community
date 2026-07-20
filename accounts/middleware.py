from django.utils import translation

class UserLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is attached to the request first
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'language_preference'):
                translation.activate(request.user.language_preference)
                request.LANGUAGE_CODE = translation.get_language()
        
        response = self.get_response(request)
        return response