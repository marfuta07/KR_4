class CacheControlMiddleware:
    """
    Middleware для клиентского кеширования.
    Добавляет заголовки Cache-Control к ответам.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Публичные страницы — кэшируем в браузере
        if request.path in ['/', '/recipients/', '/messages/', '/mailings/']:
            response['Cache-Control'] = 'public, max-age=300'  # 5 минут

        # Личные страницы (статистика, пользователи) — не кэшируем
        elif request.path.startswith('/users/') or request.path.startswith('/attempts/'):
            response['Cache-Control'] = 'private, no-cache'

        return response