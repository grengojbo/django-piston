from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication, HttpBasicSimple
from piston.authentication.oauth import OAuthAuthentication

from test_project.apps.testapp.handlers import EntryHandler, ExpressiveHandler, AbstractHandler, EchoHandler, PlainOldObjectHandler, Issue58Handler, ListFieldsHandler

auth = HttpBasicAuthentication(realm='TestApplication')

entries = Resource(handler=EntryHandler, authentication=auth)
expressive = Resource(handler=ExpressiveHandler, authentication=auth)
abstract = Resource(handler=AbstractHandler, authentication=auth)
echo = Resource(handler=EchoHandler)
popo = Resource(handler=PlainOldObjectHandler)
list_fields = Resource(handler=ListFieldsHandler)
issue58 = Resource(handler=Issue58Handler)

AUTHENTICATORS = [auth,]
SIMPLE_USERS = (('admin', 'secr3t'),
                ('admin', 'user'),
                ('admin', 'allwork'),
                ('admin', 'thisisneat'))

for username, password in SIMPLE_USERS:
    AUTHENTICATORS.append(HttpBasicSimple(realm='Test', 
                            username=username, password=password))

multiauth = Resource(handler=PlainOldObjectHandler, 
                        authentication=AUTHENTICATORS)

ouath_two_legged_api = Resource(handler=EchoHandler, authentication=OAuthAuthentication(realm='TestApplication', two_legged=True))
ouath_three_legged_api = Resource(handler=EchoHandler, authentication=OAuthAuthentication(realm='TestApplication'))

urlpatterns = patterns('',
    url(r'^entries/$', entries),
    url(r'^entries/(?P<pk>.+)/$', entries),
    url(r'^entries\.(?P<emitter_format>.+)', entries),
    url(r'^entry-(?P<pk>.+)\.(?P<emitter_format>.+)', entries),

    url(r'^issue58\.(?P<emitter_format>.+)$', issue58),

    url(r'^expressive\.(?P<emitter_format>.+)$', expressive),

    url(r'^abstract\.(?P<emitter_format>.+)$', abstract),
    url(r'^abstract/(?P<id_>\d+)\.(?P<emitter_format>.+)$', abstract),

    url(r'^echo$', echo),

    url(r'^multiauth/$', multiauth),

    # OAuth
    url(r'^oauth/', include('piston.authentication.oauth.urls')),
    url(r'^oauth/two_legged_api$', ouath_two_legged_api),
    url(r'^oauth/three_legged_api$', ouath_three_legged_api),

    url(r'^list_fields$', list_fields),
    url(r'^list_fields/(?P<id>.+)$', list_fields),
    
    url(r'^popo$', popo),
)


