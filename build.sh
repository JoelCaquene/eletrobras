    #!/usr/bin/env bash

    # Exit on error
    set -o errexit

    # Install pip and poetry
    pip install --upgrade pip

    # Install dependencies from requirements.txt
    pip install -r requirements.txt

    # Run Django migrations
    python manage.py migrate

    # Collect static files (Cloudinary handles the actual upload)
    python manage.py collectstatic --noinput

    # Create a superuser if it doesn't exist (Optional, for first deploy)
    # This is useful for initial setup, but might be removed after the first deploy
    # to prevent errors on subsequent deploys if the superuser already exists.
    # echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" | python manage.py shell

    