SITE_ID = 1
USE_I18N = True

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'django_sqlalchemy.backend'
DATABASE_NAME = ''
DJANGO_SQLALCHEMY_DBURI = "sqlite://"
DJANGO_SQLALCHEMY_ECHO = False

INSTALLED_APPS = (
    'django_sqlalchemy',
    'apps.blog',
    'apps.news',
    'apps.norelations',
    'apps.categories',
    )

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

# Of note here will be the TransactionMiddleware. 
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
)
