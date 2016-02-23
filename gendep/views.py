from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Study, Gene, Dependency  # Removed: Histotype,


def index(request): # Default is search boxes, with driver dropdown populated with driver gene_names (plus an empty name).
    driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
    # histotype_list = Histotype.objects.order_by('full_name')
    histotype_list = Dependency.HISTOTYPE_CHOICES
    study_list = Study.objects.order_by('pmid')
    context = {'driver_list': driver_list, 'histotype_list': histotype_list, 'study_list': study_list}
    return render(request, 'gendep/index.html', context)

	
def results(request):
    # For building the filter, see: http://www.nomadjourney.com/2009/04/dynamic-django-queries-with-kwargs/ 
    kwargs = {'wilcox_p__lte': 0.05}
    driver = Gene.objects.get(gene_name=request.POST['driver'])
    kwargs['driver'] = driver
    if request.POST['histotype'] != "ALL_HISTOTYPES":
      # histotype = Histotype.objects.get(histotype=request.POST['histotype'])  # if using separate Histotype database table 
      histotype = request.POST['histotype']   # When using the "choices" field.
      kwargs['histotype'] = histotype
    else: histotype = "ALL_HISTOTYPES"
    if request.POST['study'] != "ALL_STUDIES":
      study = Study.objects.get(pmid=request.POST['study'])
      kwargs['study'] = study
    else: study = "ALL_STUDIES"
    # search_driver_gene = get_object_or_404(Gene, gene_name=driver_gene_name).gene_fullname
    # dependency_list = Dependency.objects.filter(driver=driver, histotype=histotype, study=study, wilcox_p__lte=0.05).order_by('wilcox_p')
    dependency_list = Dependency.objects.filter(**kwargs).order_by('wilcox_p')
	   # was: order_by('target__gene_name'). 
	   # Only list significant hits (ie: p<=0.05)  but adding: wilcox_p<0.05 gives error "positional argument follows keyword argument"
       # was: study__pmid=request.POST['study']
       # [:20] use: 'target__gene_name' instead of 'target.gene_name'
    context = {'dependency_list': dependency_list, 'driver': driver, 'histotype': histotype, 'study': study}
    return render(request, 'gendep/results.html', context)


def graph(request, target_id):
    requested_target = get_object_or_404(Dependency, pk=target_id)
    return render(request, 'gendep/graph.html', {'target': requested_target})


#def graph(request, driver_name):
#    return HttpResponse("You're looking at the graph for driver %s." % driver_name)

#def results(request, question_id):
#    response = "You're looking at the results of question %s."
#    return HttpResponse(response % question_id)

#def vote(request, question_id):
#    return HttpResponse("You're voting on question %s." % question_id)

