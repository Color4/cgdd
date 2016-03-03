from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Study, Gene, Dependency  # Removed: Histotype,
import json # For ajax for the jquery autocomplete search box
import math # For ceil()

# This django logging is configured in settings.py and is based on: http://ianalexandr.com/blog/getting-started-with-django-logging-in-5-minutes.html
#import logging
#logger = logging.getLogger(__name__)
#def log(): logger.debug("this is a debug message!")
#def log_error(): logger.error("this is an error message!!")


def index(request): # Default is search boxes, with driver dropdown populated with driver gene_names (plus an empty name).
    driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
    # histotype_list = Histotype.objects.order_by('full_name')
    histotype_list = Dependency.HISTOTYPE_CHOICES
    study_list = Study.objects.order_by('pmid')
    dependency_list = None # For now.

    # current_url = request.get_full_path() # To display the host in title for developing on lcalhost or pythonanywhere server.
    # current_url = request.build_absolute_uri()
    #current_url =  request.META['SERVER_NAME']
    current_url =  request.META['HTTP_HOST']

    # Optionally could add locals() to the context to pass all local variables, eg: return render(request, 'app/page.html', locals())
    context = {'driver_list': driver_list, 'histotype_list': histotype_list, 'study_list': study_list, 'dependency_list': dependency_list, 'current_url': current_url}
    return render(request, 'gendep/index.html', context)


def get_drivers(request):
    # View for the driver_jquery search box.
    if request.is_ajax():
        q = request.GET.get('term', '')  #  jQuery autocomplete sends the query as "term" and it expects back three fields: id, label, and value. It will use those to display the label and then the value to autocomplete each driver gene.
        # driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
        drivers = Gene.objects.filter(is_driver=True, gene_name__icontains = q)[:20]
        # ADD: full_name__icontains = q or prev_names__icontains = q or synonyms__icontains = q
        results = []
        for d in drivers:
            d_json = {}
            d_json['id'] = d.gene_name  # But maybe this needs to be an integer? 
            d_json['label'] = d.gene_name
            d_json['value'] = d.gene_name + ' ' + d.full_name + ' ' + d.synonyms + ' ' + d.prev_names
            results.append(d_json)
        data = json.dumps(results)
        # Alternatively use: return HttpResponse(simplejson.dumps( [drug.field for drug in drugs ]))
        # eg: format is:
        # [ {"id": "3", "value":"3","label":"Matching employee A"},
        #   {"id": "5", "value":"5","label":"Matching employee B"},
        # ]
    # data = json.dumps(list(Town.objects.filter(name__icontains=q).values('name')))
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def ajax_results(request):
    # View for the dependency search result table.
    # Ajax sends four fields: driver, histotype, pmid, start(row for pagination):
    mimetype = 'text/html' # was: 'application/json'
    request_method = request.method # 'POST' or 'GET'
    if request_method != 'POST': return HttpResponse('Expected a POST request, but got a %s request' %(request_method), mimetype)

    if not request.is_ajax(): return HttpResponse('fail', mimetype)

    driver = request.POST.get('driver', "")  # It's an ajax POST request, rather than the usual ajax GET request
    if driver == "": return HttpResponse('Error: Driver must be specified', mimetype)
    # driver = None if driver == '' else Gene.objects.get(gene_name=driver)
    driver = Gene.objects.get(gene_name=driver)
    if driver is None: return HttpResponse('Driver NOT found in Gene table', mimetype)
    gene_weblinks = driver.external_links('|')

    # As Query Sets are lazy, so can build query and evaluated once at end:
    q = Dependency.objects.filter(wilcox_p__lte=0.05)
    q = q.filter( driver = driver )  # q = q.filter( driver__gene_name = driver )

    histotype = request.POST.get('histotype', "ALL_HISTOTYPES")
    if histotype != "ALL_HISTOTYPES":
        q = q.filter( histotype = histotype )
        histotype_full_name = Dependency.histotype_full_name(histotype)
    else: 
        histotype_full_name = "All histotypes"

    study = request.POST.get('study', "ALL_STUDIES")
    if study != "ALL_STUDIES":
        study = Study.objects.get(pmid=study)
        q = q.filter( study = study )

    start = request.POST.get('start', "1") # Start at 1, and increment by 20
    numrows = request.POST.get('numrows', "100") # If not specified then returns all rows - but maybe should set a maximum of 100 for now, as in final database could return whole database
    # Probably faster making just one SQL database query, even with the joins, eg:
    #        if study != "ALL_STUDIES": q = q.filter( study__pmid = study )
    numrows = int(numrows)
    max_rows_in_query = q.count()
    slice_start = int(start)-1
    slice_end = slice_start + int(numrows)
    if slice_end > max_rows_in_query: slice_end = max_rows_in_query
    dependency_list = q.order_by('wilcox_p')[slice_start:slice_end]
	   # was: order_by('target__gene_name'). 
	   # Only list significant hits (ie: p<=0.05)  but adding: wilcox_p<0.05 gives error "positional argument follows keyword argument"
       # was: study__pmid=request.POST.get('study')
       # [:20] use: 'target__gene_name' instead of 'target.gene_name'

    #current_url =  request.META['SERVER_NAME']
    current_url =  request.META['HTTP_HOST']

    # Need to finish this:
    page_num = 1 + int(slice_start/numrows) # eg. At start=1, page=1+(1-1)/20 =1; At start=21, page=1+(21-1)/20 =2
    max_pages = math.ceil( max_rows_in_query/numrows )

    context = {'dependency_list': dependency_list, 'driver': driver, 'histotype': histotype, 'histotype_full_name': histotype_full_name, 'study': study, 'gene_weblinks': gene_weblinks, 'start': start, 'numrows': numrows, 'page_num': page_num, 'max_pages': max_pages, 'current_url': current_url}
    return render(request, 'gendep/ajax_results.html', context, content_type=mimetype) #  ??? .. charset=utf-8"

        # Expects back the columns in the results table. 
        # driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
"""
        results = []
        for d in drivers:
            d_json = {}
            d_json['id'] = d.gene_name  # But maybe this needs to be an integer? 
            d_json['label'] = d.gene_name
            d_json['value'] = d.gene_name + ' ' + d.full_name + ' ' + d.synonyms + ' ' + d.prev_names
            results.append(d_json)
        data = json.dumps(results)
        # Alternatively use: return HttpResponse(simplejson.dumps( [drug.field for drug in drugs ]))
        # eg: format is:
        # [ {"id": "3", "value":"3","label":"Matching employee A"},
        #   {"id": "5", "value":"5","label":"Matching employee B"},
        # ]
    # data = json.dumps(list(Town.objects.filter(name__icontains=q).values('name')))
    else:
        data = 'fail'

    return HttpResponse(data, mimetype)
"""

def results(request):
    # For building the filter, see: http://www.nomadjourney.com/2009/04/dynamic-django-queries-with-kwargs/ 
    # request_method = request.method # 'POST' or 'GET'
    kwargs = {'wilcox_p__lte': 0.05} 
    driver = Gene.objects.get(gene_name=request.POST.get('driver')) # POST.get('..') will return a None if the 'driver' isn't in the post from the form. Could specify a default to get(.., default)
    kwargs['driver'] = driver
    if request.POST.get('histotype') != "ALL_HISTOTYPES":
      # histotype = Histotype.objects.get(histotype=request.POST.get('histotype'))  # if using separate Histotype database table 
      histotype = request.POST.get('histotype')   # When using the "choices" field.
      kwargs['histotype'] = histotype
      histotype_full_name = Dependency.histotype_full_name(histotype)
    else:
      histotype = "ALL_HISTOTYPES"
      histotype_full_name = "All histotypes"
    if request.POST.get('study') != "ALL_STUDIES":
      study = Study.objects.get(pmid=request.POST.get('study'))
      kwargs['study'] = study
    else: study = "ALL_STUDIES"
    # Instead of using the kwargs above, can just use (as the queries are lazy and aren't evaluated until query os finally run): https://docs.djangoproject.com/es/1.9/topics/db/queries/
    # q = Entry.objects.filter(headline__startswith="What")
    # q = q.filter(pub_date__lte=datetime.date.today())
    # q = q.exclude(body_text__icontains="food")
    # print(q)
    
    # search_driver_gene = get_object_or_404(Gene, gene_name=driver_gene_name).gene_fullname
    # dependency_list = Dependency.objects.filter(driver=driver, histotype=histotype, study=study, wilcox_p__lte=0.05).order_by('wilcox_p')
    dependency_list = Dependency.objects.filter(**kwargs).order_by('wilcox_p')
	   # was: order_by('target__gene_name'). 
	   # Only list significant hits (ie: p<=0.05)  but adding: wilcox_p<0.05 gives error "positional argument follows keyword argument"
       # was: study__pmid=request.POST.get('study')
       # [:20] use: 'target__gene_name' instead of 'target.gene_name'
    context = {'dependency_list': dependency_list, 'driver': driver, 'histotype': histotype, 'histotype_full_name': histotype_full_name, 'study': study}
    return render(request, 'gendep/results.html', context)


def graph(request, target_id):
    requested_target = get_object_or_404(Dependency, pk=target_id)
    return render(request, 'gendep/graph.html', {'target': requested_target})

def show_study(request, pmid):
    requested_study = get_object_or_404(Study, pk=pmid)
    # requested_study = get_object_or_404(Study, pk='Pending001') # Temportary for now.
    return render(request, 'gendep/study.html', {'study': requested_study})

def about(request):
    return render(request, 'gendep/about.html')

def drivers(request):
    driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
    context = {'driver_list': driver_list}
    return render(request, 'gendep/drivers.html')

def studies(request):
    study_list = Study.objects.order_by('pmid')
    context = {'study_list': study_list}
    return render(request, 'gendep/studies.html', context)

def contact(request):
    return render(request, 'gendep/contact.html')


#def graph(request, driver_name):
#    return HttpResponse("You're looking at the graph for driver %s." % driver_name)

#def results(request, question_id):
#    response = "You're looking at the results of question %s."
#    return HttpResponse(response % question_id)

#def vote(request, question_id):
#    return HttpResponse("You're voting on question %s." % question_id)

