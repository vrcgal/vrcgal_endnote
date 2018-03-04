from django.apps import AppConfig
from django.conf import settings

from elasticsearch_dsl.connections import connections


class ElasticAppConfig(AppConfig):
    name = 'elastic_app'

    def ready(self):
        connections.configure(**settings.ES_CONNECTIONS)
