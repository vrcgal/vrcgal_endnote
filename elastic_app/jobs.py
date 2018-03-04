import logging
import os
import time
import sys

from django.core.exceptions import ValidationError
from django.conf import settings

from bs4 import BeautifulSoup

from elasticsearch_dsl.connections import connections
from elasticsearch.helpers import streaming_bulk

from .models import Citation, UploadFailure

index = 'citations'
doc_type = 'citation'

logger = logging.getLogger(__name__)


def process_upload(filepath):
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, 'lxml-xml')

    records = soup.find_all('record')
    citations = []
    missing_text = '<missing>'
    key_word_limit = 5

    # TODO: Should clear per user not all UploadFailures
    # Clear Upload failures
    # UploadFailure.objects.delete()

    for record in records:
        keywords = missing_text
        # if record.keywords is not None and len(record.keywords) > 0:
        #     keywords = '; '.join(record.keywords[:key_word_limit])

        titles = record.titles.title.get_text() if record.titles is not None else missing_text # noqa E501
        keywords = keywords
        journal = record.periodical.get_text() if record.periodical is not None else missing_text, # noqa E501
        volume = record.volume.get_text() if record.volume is not None else missing_text # noqa E501
        if record.dates and record.dates.year:
            date = record.dates.year.get_text()
        else:
            date = missing_text

        data = {
            'title': titles,
            'keywords': keywords,
            'journal': journal,
            'volume': volume,
            'date': date
        }

        try:
            citation = Citation.create_from_record(data)
            citation.full_clean()

            if titles == missing_text:
                raise ValidationError('must have a title')

            citations.append(citation)
        except ValidationError as e:
            print(e.message_dict)
            UploadFailure.objects.create(
                title=titles,
                reason=str(e)
            )

    Citation.objects.bulk_create(citations)

    os.remove(filepath)

    # Now index the data in ES
    index_data(Citation)


def index_data(model, report_every=100):
    es = connections.get_connection()
    name = model._meta.verbose_name

    print('Indexing {}: '.format(name))

    start = time.time()
    cnt = 0
    for _  in streaming_bulk(
        es,
        (m.to_search().to_dict(True) for m in model.objects.all().iterator()),
        index=settings.ES_INDEX,
        doc_type=name.lower(),
    ):
        cnt += 1
        if cnt % report_every:
            print(cnt)
            sys.stdout.flush()

    print('DONE\nIndexing %d %s in %.2f seconds' % (
        cnt, name, time.time() - start
    ))
