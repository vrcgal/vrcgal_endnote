import binascii
import django_rq
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.list import ListView

from .forms import XmlForm, SearchForm
from .jobs import process_upload
from .models import Citation, UploadFailure
from .search import CitationSearch


class CitationList(ListView):
    model = Citation
    paginate_by = 100
    extra_context = {
        'form': SearchForm(),
        'has_failures': UploadFailure.objects.count() > 0
    }

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        for key, value in self.extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
        return context


class UploadFailureList(ListView):
    model = UploadFailure
    paginate_by = 100


def search(request):
    # Handle file upload
    failure_count = UploadFailure.objects.count()
    form = SearchForm(request.GET)
    citations = []
    if form.is_valid():
        title = request.GET.get('search')
        bs = CitationSearch(title)
        results = bs.execute()
        hits = [hit['_id'] for hit in results['hits']['hits']]
        clauses = ' '.join(
            ['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(hits)]
        )
        ordering = 'CASE %s END' % clauses

        citations = Citation.objects.filter(pk__in=hits).extra(
            select={'ordering': ordering}, order_by=('ordering',)
        )

    return render(
        request,
        'elastic_app/citation_list.html',
        {
            'object_list': citations,
            'has_failures': failure_count > 0,
            'form': SearchForm()
        }
    )


def upload(request):
    # Handle file upload
    if request.method == 'POST':
        form = XmlForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['docfile']

            _handle_uploaded_file(file)

            return HttpResponseRedirect(reverse('app:citation-list'))
    else:
        form = XmlForm()  # A empty, unbound form

    return render(
        request,
        'elastic_app/upload.html',
        {'form': form}
    )


def _handle_uploaded_file(f):
    # TODO: Add S3 support for file storage
    file_path = '/tmp/{}.xml'.format(str(binascii.b2a_hex(os.urandom(15))))
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Enqueue for further processing
    django_rq.enqueue(process_upload, file_path)
