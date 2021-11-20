import logging
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static, serve
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view


# Get an instance of a logger
logger = logging.getLogger(__name__)


patterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls', namespace='user')),
    path('social/', include('social_auth.urls', namespace='social_auth')),
]

extrapatterns = [
    # api docs
    path('openapi', get_schema_view(title='Drf Starter',
                                    description='DRF STARTER', version='1.0.0'), name='openapi'),

    path('docs/', TemplateView.as_view(template_name='api-doc.html',
         extra_context={'schema_url': 'openapi'})),

    path('redoc/', TemplateView.as_view(template_name='redoc.html',
         extra_context={'schema_url': 'openapi'})),

    # django_summernote
    path('summernote/', include('django_summernote.urls')),

    # React static file serve
    # re_path('(^(?!(api|media|static)).*$)', TemplateView.as_view(template_name='index.html')),
]


if settings.DEBUG:
    logger.info('#####DEBUG MODE#####')
    staticpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    logger.info('#####PRODUCTION MODE#####')
    staticpatterns = [
        re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
        re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
    ]

urlpatterns = patterns + staticpatterns + extrapatterns


# https://docs.djangoproject.com/en/dev/topics/http/views/#customizing-error-views
handler404 = 'user.views.error_404'