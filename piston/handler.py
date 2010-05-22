import warnings

from utils import rc
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from django.db.models.query import QuerySet

typemapper = { }
handler_tracker = [ ]

class HandlerMetaClass(type):
    """
    Metaclass that keeps a registry of class -> handler
    mappings.
    """
    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)

        def already_registered(model, anon):
            for k, (m, a) in typemapper.iteritems():
                if model == m and anon == a:
                    return k

        if hasattr(new_cls, 'model') and new_cls.model is not None:
            if already_registered(new_cls.model, new_cls.is_anonymous):
                if not getattr(settings, 'PISTON_IGNORE_DUPE_MODELS', False):
                    warnings.warn("Handler already registered for model %s, "
                        "you may experience inconsistent results." % new_cls.model.__name__)

            typemapper[new_cls] = (new_cls.model, new_cls.is_anonymous)
        else:
            typemapper[new_cls] = (None, new_cls.is_anonymous)

        if name not in ('BaseHandler', 'AnonymousBaseHandler'):
            handler_tracker.append(new_cls)

        return new_cls

class BaseHandler(object):
    """
    Basehandler that gives you CRUD for free.
    You are supposed to subclass this for specific
    functionality.

    All CRUD methods (`read`/`update`/`create`/`delete`)
    receive a request as the first argument from the
    resource. Use this for checking `request.user`, etc.
    """
    __metaclass__ = HandlerMetaClass

    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    anonymous = is_anonymous = False
    exclude = ( 'id', )
    fields =  ( )

    def flatten_dict(self, dct):
        return dict([ (str(k), dct.get(k)) for k in dct.keys() ])

    def has_model(self):
        return hasattr(self, 'model') or hasattr(self, 'queryset')

    def queryset(self, request):
        return self.model.objects.all()

    def value_from_tuple(tu, name):
        for int_, n in tu:
            if n == name:
                return int_
        return None

    def exists(self, **kwargs):
        if not self.has_model():
            raise NotImplementedError

        try:
            self.model.objects.get(**kwargs)
            return True
        except self.model.DoesNotExist:
            return False

    def read(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        pkfield = self.model._meta.pk.name

        if pkfield in kwargs:
            try:
                return self.queryset(request).get(pk=kwargs.get(pkfield))
            except ObjectDoesNotExist:
                return rc.NOT_FOUND
            except MultipleObjectsReturned: # should never happen, since we're using a PK
                return rc.BAD_REQUEST
        else:
            return self.queryset(request).filter(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        attrs = self.flatten_dict(request.data)

        try:
            inst = self.queryset(request).get(**attrs)
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            inst = self.model(**attrs)
            inst.save()
            return inst
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY

    def update(self, request, *args, **kwargs):
        if not self.has_model():
            return rc.NOT_IMPLEMENTED

        pkfield = self.model._meta.pk.name

        if pkfield not in kwargs:
            # No pk was specified
            return rc.BAD_REQUEST

        try:
            inst = self.queryset(request).get(pk=kwargs.get(pkfield))
        except ObjectDoesNotExist:
            return rc.NOT_FOUND
        except MultipleObjectsReturned: # should never happen, since we're using a PK
            return rc.BAD_REQUEST

        attrs = self.flatten_dict(request.data)
        for k,v in attrs.iteritems():
            setattr( inst, k, v )

        inst.save()
        return rc.ALL_OK

    def delete(self, request, *args, **kwargs):
        if not self.has_model():
            raise NotImplementedError

        try:
            inst = self.queryset(request).get(*args, **kwargs)

            inst.delete()

            return rc.DELETED
        except self.model.MultipleObjectsReturned:
            return rc.DUPLICATE_ENTRY
        except self.model.DoesNotExist:
            return rc.NOT_HERE

class AnonymousBaseHandler(BaseHandler):
    """
    Anonymous handler.
    """
    is_anonymous = True
    allowed_methods = ('GET',)

class PaginatedCollectionBaseHandler(BaseHandler):
    """
    A handler for paginated queries. Allows for configurable offset (start)
    and count on the url itself. Does limit the maximum number of objects to be fetched 
    in order not to overload the server if a client asks for way to many resources.
    Uses the Atom Publication Protocol suggestion of having next and previous 
    information as links.
    Furthermore, if you want to further filter the QuerySet, you can set the 'resources'
    property to the desired queryset.
    """
    # the maximum number of resources  per request, to avoid
    # bringing the server down
    max_resources_per_page = 20
    resource_name = None
    resources = None
    model = None 
    def read(self, request,  start = None, limit=None):
        '''
        Prepares a response with the queryset objects, a next and previous link 
        and a total count of items
        '''
        from django.core.urlresolvers import resolve, reverse
        from urllib import urlencode
        # use request.GET as a fallback for start and count:
        slices_in_querystring=False
        if start is None:
            slices_in_querystring = True
            try:
                start = request.GET["start"]
            except KeyError:
                raise KeyError("Paginated resources must be passed a 'start' parameter.")
        if limit is None:
            limit = request.GET.get("limit", PaginatedCollectionBaseHandler.max_resources_per_page)
        # just make sure we have ints, and no insane values 
        start = int(start)
        limit = min(int(limit), PaginatedCollectionBaseHandler.max_resources_per_page)
        if self.resource_name is None:
            if self.model:
                resource_name = unicode(self.model._meta.verbose_name_plural)
            else:
                resource_name = "resource"
        # find out what resources to use, e model (then a queryset), a callable or a regular sequence
        # and also how to count the total number of objects (qs.count vs regular len(seq)
        resources = self.resources
        if resources is None:
            resources = self.model.objects.all() 
            total = self.model.objects.count()
        elif callable(resources):
            resources = resources()
            total = len(resources)
        elif isinstance(resources, QuerySet):
            total = resources.count()
        else:
            #print "in len"
            total = len (resources)
        # the queryset proper
        end = min (total, start + count)
        # in order to generate next and previous links, 
        # we need to reverse the url and resolve again
        # with the new limits
        view, args, kwargs =  resolve(request.path)
        next_start = start + limit
        next_end = min (total, next_start + limit)
        # reverse urls ignore the querystring so we must reconstruct those
        if slices_in_querystring:
            query_dict = dict([part.split('=') for part in request.META["QUERY_STRING"].split('&')]) 
        # figure out next links
        if next_start >= total:
            next = ""
        else:
            if slices_in_querystring is False:
                kwargs["start"] = next_start
            next = request.build_absolute_uri(reverse(view, None, args, kwargs))
            if slices_in_querystring:
                query_dict["start"] = next_start
                new_query = urlencode(query_dict)
                next = "%s?%s" % (next,new_query)


        if start - limit >= 0:
            if slices_in_querystring is False:
                kwargs["start"] = start - limit
            previous = request.build_absolute_uri(reverse(view, None, args, kwargs))
            if slices_in_querystring:
                query_dict["start"] = start - limit
                new_query = urlencode(query_dict)
                previous = "%s?%s" % (previous,new_query)
        else:
            previous = ""

        data = {}

        data[resource_name] =  resources[start:end]
        data["next"] = next
        data["previous"] = previous
        data["count"]  = total
        return data