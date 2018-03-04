from django.conf import settings
from datetime import datetime
from elasticsearch_dsl import DocType, Date, FacetedSearch, Index, \
    Q, TermsFacet, Text


class Citation(DocType):
    title = Text()
    keywords = Text()
    journal = Text()
    volume = Text()
    date = Date()
    created_at = Date()
    updated_at = Date()

    class Meta:
        index = 'citations'

    def save(self, **kwargs):
        self.created_at = datetime.now()
        return super().save(**kwargs)


# create an index and register the doc types
index = Index(settings.ES_INDEX)
index.settings(number_of_shards=1, number_of_replicas=0)
index.doc_type(Citation)


class CitationSearch(FacetedSearch):
    index = settings.ES_INDEX
    doc_types = [Citation, ]
    fields = ['title', 'journal']

    def query(self, search, query):
        if not query:
            return search
        q = Q(
            'multi_match',
            fields=['title^10', 'journal'],
            query=query
        )

        # take the rating field into account when sorting
        search = search.query(
            'function_score',
            query=q,
        )

        return search

    def highlight(self, search):
        return search
