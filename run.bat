pip install -e .
python ./manage.py migrate --noinput
python ./manage.py collectstatic --noinput
python ./manage.py runserver localhost:8000