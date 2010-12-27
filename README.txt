~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Getting OAuth Working with django-piston
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a bare-skeleton Django application which demonstrates how you can
add an API to your own applications.

It's a simple blog application, with a "Blogpost" model, with an API on top
of it. It has a fixture which contains a sample user (used as author and
for auth) and a couple of posts.
You can get started like so:

$ cd django-piston/examples/oauth
$ mkvirtualenv piston
$ easy_install pip
$ pip install -U -E ~/.virtualenvs/piston -r ./req-piston.txt

$ cdsitepackages
$ vim easy-install.pth
$ vim django-piston.egg-link
$ deactivate
$ cd django-piston/examples/oauth
$ workon piston
$ ./manage.py syncdb  --settings=settings (answer "no" when it asks for superuser creation)
$ ./run.sh

Now, the admin and test user has authentication info:

Username: admin
Password: admin

Username: testuser
Password: foobar

Running
-------
    "You are unauthenticated. (API protected by OAuth)." In browser:
    http://localhost:8000/api/posts.json

Running Client
--------------
    # make sure "oauth_client.py" has correct hostname
    $ python oauth_client.py #create new token/secret, put "oauth_token" link in browser, "what is PIN? aka 'oauth_verifier'"



