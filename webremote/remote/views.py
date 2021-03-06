# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from remote.models import Document
from remote.forms import DocumentForm

from django.conf import settings

def index(request):
    context = {'frameidentity': settings.FRAMEIDENTITY}
    return render_to_response('remote/index.html',context)
    
def list(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile = request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('remote.views.list'))
    else:
        form = DocumentForm() # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'remote/list.html',
        {'documents': documents, 'form': form},
        context_instance=RequestContext(request)
    )
