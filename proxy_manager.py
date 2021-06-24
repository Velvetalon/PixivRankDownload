import settings


def get_proxy():
    if settings.USE_PROXY:
        return {
            'http': settings.PROXY_HOST + ":" + str(settings.PROXY_PORT),
            'https': settings.PROXY_HOST + ":" + str(settings.PROXY_PORT)
        }
    else:
        return {}
