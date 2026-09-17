web: python dashboard/manage.py collectstatic --noinput && python dashboard/manage.py migrate && gunicorn --chdir dashboard dashboard.wsgi:application --bind 0.0.0.0:$PORT
