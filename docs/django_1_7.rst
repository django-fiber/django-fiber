Django 1.7 migrations
==================

Django-fiber 1.0 supports Django 1.7. This means that it also uses the new `Django 1.7 migrations`_.

.. _Django 1.7 migrations: https://docs.djangoproject.com/en/1.7/topics/migrations/

* The South migrations are removed. If you want to use the old South migrations, then read below.
* There are no database changes between the previous version (0.13) and 1.0.

Migration from Django-fiber 0.13
--------------------------------

* You want to migrate from Django-fiber 0.13 to 1.0
* You want to use Django 1.7

Good news! Your database is up-to-date. There are no new migrations.

You still should fake the new migrations. Also see `upgrading from south`_.

::

    python manage.py migrate --fake fiber

.. _upgrading from south: https://docs.djangoproject.com/en/1.7/topics/migrations/#upgrading-from-south


Migration from Django-fiber <= 0.12.2
---------------------------------

* You want to to migrate from Django-fiber <= 0.12.2 to 1.0
* You want to use Django 1.7

You should first upgrade to Django-fiber 0.13:

::

    pip install -U django-fiber==0.13

Do not yet update to Django 1.7.

Apply the migrations:

::

    python manage.py migrate fiber

You can now upgrade to Django-fiber 1.0 and Django 1.7.


Other variations
----------------

If you want to keep using Django <= 1.6:

* You want to migrate from Django-fiber 0.13 to 1.0.

You don't have to do anything because your database is up-to-date.

* You migrate from Django-fiber <= 0.12.2 to 1.0.
 
You should first upgrade to Django-fiber 0.13 and apply the South migrations.

