from os import getenv

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DB_NAME', 'careernavigator'),
        'USER': getenv('DB_USER', 'careernavigator'),
        'PASSWORD': getenv('DB_PASSWORD'),
        'HOST': getenv('DB_HOST'),
        'PORT': int(getenv('DB_PORT', '5432')),
    }
}
