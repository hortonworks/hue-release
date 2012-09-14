from tastypie.resources import ModelResource
from .models import Jobs

__all__ = ['JobsResource']


class JobsResource(ModelResource):

    class Meta:
        queryset = Jobs.objects.all()
        resource_name = 'jobs'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        include_resource_uri = False
