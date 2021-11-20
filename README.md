# Drf Starter Social

## Installation

Make sure you have python3.8/+ installed.

```bash
pip install -r requirements.txt
```
Create a file in the project root folder named .env following the .env.template file

After dependencies are installed migrate your database.

```bash
python manage.py makemigrations
python manage.py migrate
```

Create a superuser.

```bash
python manage.py createsuperuser
```

Run server.

```bash
python manage.py runserver
```

Now, navigate to the docs.

http://localhost:8000/docs/

##Have Fun!

##Please do not hesitate to open an issue or create a pull request.
