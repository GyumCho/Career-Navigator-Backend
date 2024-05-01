# CareerNavigator Backend

## Development Installation

Required packages: Python

### Linux

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Windows

```bat
python3 -m venv .venv
.venv/Scripts/activate.bat
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Production Installation

It is recommended to run this in Docker. To build and run the docker image, run:

```bash
docker build . -t careernavigator:latest
docker run -p 8000:8000 -e DJANGO_SECRET_KEY=SOME_RANDOM_STRING_THAT_IS_CONSISTENT_BUT_VERY_SECRET --mount type=bind,source="db.sqlite3",target="/project/db.sqlite3" careernavigator:latest
```
