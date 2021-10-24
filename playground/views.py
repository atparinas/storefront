from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType

from store.models import Product
from tags.models import TaggedItem


def say_hello(request):
    
    query_set = TaggedItem.objects.get_tags_for(Product, 1)


    return render(request, 'hello.html', {'tags' : list(query_set)})