from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Gene, Dependency


def index(request): # Default is search boxes, with driver dropdown populated with driver gene_names (plus an empty name).
    # context = RequestContext(request)
    driver_list = Gene.objects.filter(is_driver==True).order_by('gene_name')  # but just need gene_names for now.
    context = {'driver_list': target_list}  # maybe add histotype later.
    return render(request, 'gendep/index.html', context)  # or render_to_response( .... ) ?

def results(request):
    # context = RequestContext(request)
    search_driver_gene_name = request.POST['search_driver_gene']
    driver_fullname = Gene.objects.get(gene_name=search_driver_gene_name).gene_fullname
    # search_driver_gene = get_object_or_404(Gene, gene_name=search_driver_gene_name).gene_fullname
    dependency_list = Dependency.objects.filter(driver__gene_name=search_driver_gene_name, 
                                                histotype=request.POST['search_histotype'], 
                                                study_pmid__pmid=request.POST['search_study']
                                                ).order_by('target__gene_name')  # [:20] use study_pmid__pmid instaed of study_pmid.pmid, AND 'target__gene_name' instead of 'target.gene_name'
    # ADD: 'study_list': study and histotype_list below:
    context = {'dependency_list': dependency_list, 'driver_fullname': driver_fullname}
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

