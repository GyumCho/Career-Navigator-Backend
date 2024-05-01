python manage.py migrate
python manage.py createcachetable

python manage.py collectstatic --noinput

cd /project
# exec uvicorn \
#     --host 0.0.0.0\
#     --workers ${WORKER_THREADS:-4} \
#     --h11-max-incomplete-event-size 32768\
#     careernavigator.asgi:application

python manage.py runserver 0.0.0.0:8000
