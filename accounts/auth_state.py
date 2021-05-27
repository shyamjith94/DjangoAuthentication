from django.conf import settings

from utils.shortcuts import import_module

backend_cls = import_module(settings.JWT_AUTH_BACKEND_CLS)
auth_handler_cls = import_module(settings.JWT_AUTH_HANDLER_CLS)


auth_handler = auth_handler_cls(backend=backend_cls)
