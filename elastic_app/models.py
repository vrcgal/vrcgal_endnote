from django.db import models
from django.db.models.signals import post_save, pre_delete

from .search import Citation as CitationDoc


class Citation(models.Model):
    title = models.CharField(max_length=512)
    keywords = models.CharField(max_length=512)
    journal = models.CharField(max_length=512)
    volume = models.CharField(max_length=200)
    date = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def create_from_record(cls, record):
        return cls(
            title=record['title'],
            keywords=record['keywords'],
            journal=record['journal'],
            volume=record['volume'],
            date=record['date'],
        )

    def to_search(self):
        d = {
            'id': self.pk,
            'title': self.title,
            'journal': self.journal,
            'keywords': [word for word in self.keywords.split(';')],
            'volume': self.volume,
            'date': self.date
        }

        return CitationDoc(
            meta={'id': d['id']},
            **d
        )

    def __str__(self):
        return "{0}. {1} {2}: {3} ({4})".format(
            self.title,
            self.journal,
            self.date,
            self.volume,
            self.keywords
        )


class UploadFailure(models.Model):
    title = models.CharField(max_length=512)
    reason = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Title: {0} -- Reason: {1}".format(
            self.title,
            self.reason
        )


# Register search callbacks
def update_search(instance, **kwargs):
    instance.to_search().save()


def remove_from_search(instance, **kwargs):
    instance.to_search().delete()


post_save.connect(update_search, sender=Citation)
pre_delete.connect(remove_from_search, sender=Citation)
