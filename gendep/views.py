import csv, time
import json # For ajax for the jquery autocomplete search box
import math # For ceil()
from urllib.request import Request, urlopen
from urllib.error import  URLError
from datetime import datetime # For get_timming() and log_comment()
import requests # for Enrichr and mailgun email server
import ipaddress # For is_valid_ip()

from django.http import HttpResponse #, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache  # To cache previous results. NOTE: "To provide thread-safety, a different instance of the cache backend will be returned for each thread."
from django.utils import timezone # For log_comment(), with USE_TZ=True in settings.py, and istall "pytz"
from django.db.models import Q # Used for get_drivers()
         
from .models import Study, Gene, Dependency, Comment  # Removed: Histotype,

# Optionally use Django logging during development and testing:
# This Django logging is configured in settings.py and is based on: http://ianalexandr.com/blog/getting-started-with-django-logging-in-5-minutes.html
#import logging
#logger = logging.getLogger(__name__)
#def log(): logger.debug("this is a debug message!")
#def log_error(): logger.error("this is an error message!!")

# Mime types for the responses:
html_mimetype = 'text/html; charset=utf-8'
json_mimetype = 'application/json; charset=utf-8'
csv_mimetype  = 'text/csv; charset=utf-8' # can be called: 'application/x-csv' or 'application/csv'
tab_mimetype  = 'text/tab-separated-values; charset=utf-8'
plain_mimetype ='text/plain; charset=utf-8'
#excel_minetype ='application/vnd.ms-excel'
excel_minetype ='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' # for xlsx format?

# Alternatively can use separate parameter in HtmlResponse: charset='UTF-8' instead of including 'charset=utf-8' in the content_type

# Enricher URL:
ENRICHR_BASE_URL = 'http://amp.pharm.mssm.edu/Enrichr/'

def post_or_get_from_request(request, name):
    if   request.method == 'POST': return request.POST.get(name, '')
    elif request.method == 'GET':  return request.GET.get(name, '')
    else:  return ''
    
def JsonResponse(data, safe=False):
    """ Could use the Django JsonResponse but less format options, so using HtmlResponse() """
    # eg: django.http.JsonResponse(data, safe=safe)
    return HttpResponse(json.dumps(data, separators=[',',':']), content_type=json_mimetype)

def json_error(message, status_code='1'):
    """ Sends an error message to the browser in JSON format """
    return JsonResponse( {'success': False, 'error': status_code, 'message': message } ) # eg: str(exception)

def is_search_by_driver(search_by):
    """ Checks if the 'search_by' parameter is valid, returning True if the dependency search is by driver """
    if   search_by == 'driver': return True
    elif search_by == 'target': return False
    else: print("ERROR: **** Invalid search_by: '%s' ****" %(search_by))

def get_study_shortname_from_study_list(study_pmid, study_list):
    if (study_pmid is None) or (study_pmid == ''):
        return ''
    if study_pmid=="ALL_STUDIES":
        return "All studies"
    try:    
        study = study_list.get(study_pmid=study.pmid)
#   Or iterate through the list:        
#   for study in study_list:
#       if study_pmid == study.pmid:
        return study.short_name
    except ObjectDoesNotExist: # Not found by the objects.get()
        print("WARNING: '"+study_pmid+"' NOT found in database so will be ignored")
        return '' # ie. if study_pmid parameter value not found then ignore it.
        
        
        
def get_timing(start_time, name, time_list=None):
    """ Prints the time taken by functions, to help optimise the code and SQL queries.
    The start_time parameter value should be obtained from: datetime.now()
    Optionally if 'time_list' is passed then an array of timings is added to this list that can then be sent to Webbrowser console via JSON. A python list (array) is used (rather than a dictionary) so will preserve the order of elements. """
    duration = datetime.now() - start_time # This duration is in milliseconds
    # To print results in server log, use:
    # print( "%s: %s msec" %(name,str(duration)))  # or use: duration.total_seconds()
    if time_list is not None:
        if not isinstance(time_list, list):
            print("ERROR: get_timings() 'time_list' parameter is not a list")
        #if name in time_dict: print("WARNING: Key '%s' is already in the time_dict" %(name))
        time_list.append({name: str(duration)})
    return datetime.now()


    
def index(request, search_by = 'driver', gene_name='', histotype_name='', study_pmid=''):
    """ Sets the javascript arrays for driver, histotypes and studies within the main home/index page.
    As the index page can be called with specified values, eg: '.../driver/ERBB2/PANCAN/26947069/'
    Then calls the 'index.html' template to create the webpage.
    The 'search_by' is usually by driver, but for the "SearchByTarget" webpage, it will be set to 'target' """
    
    # Obtain the list of driver genes for the autocomplete box.
    # (Or for the 'Search-ByTarget' webpage, get the list of target genes).
    # This needs: (is_driver=True), not just: (is_driver)
    if is_search_by_driver(search_by):
        driver_list = Gene.objects.filter(is_driver=True).only("gene_name", "full_name", "is_driver", "prevname_synonyms").order_by('gene_name')
        target_list = []
    else: 
        target_list = Gene.objects.filter(is_target=True).only("gene_name", "full_name", "is_target", "prevname_synonyms").order_by('gene_name')
        driver_list = []

    # Retrieve the tissue, experiment type, and study data:
    histotype_list = Dependency.HISTOTYPE_CHOICES
       # Alternatively if using histotype table (in the 'models.py' instead of 'choices' list):  histotype_list = Histotype.objects.order_by('full_name')
    experimenttype_list = Study.EXPERIMENTTYPE_CHOICES
    study_list = Study.objects.order_by('pmid')
    
    # As this page could in future be called from the 'drivers' or 'targets' page, with the gene_name as a standard GET or POST parameter (instead of the Django '/gene_name' parameter option in url.py):
    if (gene_name is None) or (gene_name == ''):
        gene_name = post_or_get_from_request(request, 'gene_name')
        
    # Set the default histotype to display in the Tissues menu:
    # Previously this defaulted to PANCAN (or "ALL_HISTOTYPES"), BUT now the tissue menu is populated by javascript after the user selects driver gene:
    # if histotype_name=="": histotype_name="PANCAN"
    if histotype_name is None: histotype_name='' 
    
    # Get the study short name (to display as default in the studies menu) for the study_pmid:
    study_short_name = get_study_shortname_from_study_list(study_pmid,study_list)

    # Get host IP (or hostname) To display the host in title for developing on localhost or pythonanywhere server:
    # current_url = request.get_full_path()
    # current_url = request.build_absolute_uri()
    # current_url =  request.META['SERVER_NAME']
    current_url =  request.META['HTTP_HOST']

    # Set the context dictionary to pass to the template. (Alternatively could add locals() to the context to pass all local variables, eg: return render(request, 'app/page.html', locals())
    context = {'search_by': search_by, 'gene_name': gene_name, 'histotype_name': histotype_name, 'study_pmid': study_pmid, 'study_short_name': study_short_name, 'driver_list': driver_list, 'target_list': target_list,'histotype_list': histotype_list, 'study_list': study_list, 'experimenttype_list': experimenttype_list, 'current_url': current_url}
    return render(request, 'gendep/index.html', context)


def get_drivers(request):
    """ Returns list of driver genes in JSON format for the jquery-ui autocomplete searchbox AJAX mode """
    
    # if request.is_ajax(): # Users can also access this from API scripts so not always AJAX
    name_contains = request.GET.get('name', '')
    # jQuery autocomplete sends the query as "name" and it expects back three fields: id, label, and value, eg:
    # [ {"id": "ERBB2", "value":"ERBB2","label":"ERBB2, ...."},
    #   {"id": "ERBB3", "value":"ERBB3","label":"ERBB3, ...."},
    # ]

    # For each driver gene, the autocomplete box with display the 'label' then the 'value'.
    
    if name_contains == '':
        # Needs: (is_driver=True), not just: (is_driver)
        drivers = Gene.objects.filter(is_driver=True)
    else:    
        # drivers = Gene.objects.filter(is_driver=True, gene_name__icontains=name_contains)
        # To search in both: 'gene_name' or 'prevname_synonyms', need to use the 'Q' object:
        drivers = Gene.objects.filter(is_driver=True).filter( Q(gene_name__icontains=name_contains) | Q(prevname_synonyms__icontains=name_contains) )  # could add: | Q(full_name__icontains=name_contains)

    results = []
    for d in drivers.order_by('gene_name'):
        results.append({
            'id':    d.gene_name,
            'value': d.gene_name,
            'label': d.gene_name + ' : ' + d.full_name + ' : ' + d.prevname_synonyms
        })        
        
    # For a simpler result set could use, eg: 
    # results = list(Gene.objects.filter(gene_name__icontains=name_contains).values('gene_name'))
    
    return JsonResponse(results, safe=False) # needs 'safe=false' as results is an array, not dictionary.



def is_valid_ip(ip_address):
    """ Check validity of an IP address """
    try:
        ip = ipaddress.ip_address(u'' + ip_address)
        return True
    except ValueError as e:
        return False
    
def get_ip_address_from_request(request):
    """ Makes the best attempt to get the client's real IP or return the loopback """    
    # Based on: "easy_timezones.utils.get_ip_address_from_request": https://github.com/Miserlou/django-easy-timezones
    
    # On PythonAnywhere the loadbalancer puts the IP address received into the "X-Real-IP" header, and also passes the "X-Forwarded-For" header as a comma-separated list of IP addresses. The 'REMOTE_ADDR' contains load-balancer address.
    
    PRIVATE_IPS_PREFIX = ('10.', '172.', '192.', '127.')
    ip_address = ''
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if x_forwarded_for and ',' not in x_forwarded_for:
        if not x_forwarded_for.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_forwarded_for):
            ip_address = x_forwarded_for.strip()
    else:
        ips = [ip.strip() for ip in x_forwarded_for.split(',')]
        for ip in ips:
            if ip.startswith(PRIVATE_IPS_PREFIX):
                continue
            elif not is_valid_ip(ip):
                continue
            else:
                ip_address = ip
                break
    if not ip_address:
        x_real_ip = request.META.get('HTTP_X_REAL_IP', '') # PythonAnywhere load-balancer puts the real IP in this 'HTTP_X_REAL_IP'.
        if x_real_ip:
            if not x_real_ip.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(x_real_ip):
                ip_address = x_real_ip.strip()
    if not ip_address:
        remote_addr = request.META.get('REMOTE_ADDR', '') # On PythonAnywhere this is the load-balancer address.
        if remote_addr:
            if not remote_addr.startswith(PRIVATE_IPS_PREFIX) and is_valid_ip(remote_addr):
                ip_address = remote_addr.strip()
    if not ip_address:
        ip_address = '127.0.0.1'
    return ip_address
    
    
    
def send_an_email(emailfrom, emailto, emailreplyto, subject, text):
    """ Uses the 'mailgun.com' service (as free  PythonAnywhere accounts don't have SMTP access) """
    # mailgun.com records email in your logs: https://mailgun.com/cp/log 
    # Better to keep this API auth key in a separate file, not on github:
    response = requests.post(
        "https://api.mailgun.net/v3/sandboxfb49cd4805584358bdd5ee8d96240a09.mailgun.org/messages",
        auth=("api", "key-ff52850192b21b271260779529ebd491"),
        data={"from": emailfrom,
              "to": emailto,
              "h:Reply-To": emailreplyto,
              "subject": subject,
              "text": text
              })
    if not response.ok: print("Failed to send email as:", response.content)
    return response.ok
    

    
def log_comment(request):
    """ Log and email comments/queries from the 'contacts' page """
    # The user's input data is send by an HTML POST, not by Django url parameters as the message can be long:
    name = request.POST.get('name', '')
    emailreplyto = request.POST.get('email', '')
    comment = request.POST.get('comment', '')
    
    # Optional fields, which are currently commented out on the html template:
    #   interest = request.POST.get('interest', '')
    #   human = request.POST.get('human', '')  # Result of a simple maths test, to check user is not a web spam robot.
    
    # To store the timezone: in "cgdd/settings.py" set: USE_TZ=True    
    date = timezone.now()
    
    ip = get_ip_address_from_request(request)
        
    c = Comment.objects.create(name=name, email=emailreplyto, comment=comment, ip=ip, date=date)
        
    # Should probably check for email header injection attacks:  https://www.reddit.com/r/Python/comments/15n6dw/sending_emails_through_python_and_gmail/
    # But mailgun probably checks for this.

    emailfrom=emailreplyto # Needs to be a valid email address or might give an exception?

    # The emailto address needs to be authorised on the mailgun.com     
    emailto="cancergenetics@ucd.ie" # or: "Cancer Genetics <cancergenetics@ucd.ie>"
    #emailto="sbridgett@gmail.com"  # or: "Stephen <sbridgett@gmail.com>" for testing.

    subject="Cgenetics Comment/Query: "+str(c.id)

    # Datetime formatting: https://docs.python.org/3.5/library/datetime.html#strftime-strptime-behavior
    text = "From: "+name+" "+emailreplyto+"\nDate: " + date.strftime("%a %d %b %Y at %H:%M %Z") + "\n\n"+comment
    # https://docs.djangoproject.com/en/1.9/topics/i18n/timezones/
    
    email_sent = "Email sent to cgenetics" if send_an_email(emailfrom=emailfrom, emailto=emailto, emailreplyto=emailreplyto, subject=subject, text=text) else "Failed to send email, but your message was saved in our comments database."  # To the email could add: interest=interest

    context = {'name': name, 'email': emailreplyto, 'comment': comment, 'date': date, 'email_sent': email_sent}
    return render(request, 'gendep/log_comment.html', context, content_type=html_mimetype)
    

def get_histotype_full_name(histotype_name):
    """ Returns the human readable proper-case tissue name, eg: 
        if input is 'PANCAN' returns 'Pan cancer', or if input 'SOFT_TISSUE' returns 'Soft tissue' """
    if histotype_name == "ALL_HISTOTYPES":
        return "All tissues"
    else:
        return Dependency.histotype_full_name(histotype_name)


def get_study(study_pmid):
    """ Returns short study name (First author and year), for an imput Pub-Med Id """
    if study_pmid == "ALL_STUDIES":
        return "ALL_STUDIES"
    try:
        study = Study.objects.get(pmid=study_pmid)
    except ObjectDoesNotExist: # Not found by the objects.get()
        study = None
    return study        


def get_gene(gene_name):
    """ Returns the Gene object (row from the Gene table) for the input gene_name (eg. 'ERBB2') """
    # gene = None if gene_name == '' else Gene.objects.get(gene_name=gene_name)            
    if gene_name=='':
        return None
    try:
        gene = Gene.objects.get(gene_name=gene_name)
    except ObjectDoesNotExist: # gene_name not found by the Gene.objects.get()
        gene = None
    return gene
    
    
def build_dependency_query(search_by, gene_name, histotype_name, study_pmid, wilcox_p=0.05, order_by='wilcox_p', select_related=None):
    """ Builds the query used to extract the requested dependencies.
          search_by:      'driver' or 'target'
          gene_name:      must be sepcified and in the Genes table
          histotype_name: can be "ALL_HISTOTYPES" or a histotype in the model
          study_pmid:     can be "ALL_STUDIES" or a study pubmed id in the Study table
          wilcox_p:       the Dependency table only contains the rows with wilcox_p <=0.05 so must be same or less than 0.05
          order_by:       defaults to wilcox_p, but could be 'target_id' or 'effect_size', etc
          select_related: can be None, or a string, or a list of strings (eg: ['driver__inhibitors', 'driver__ensembl_protein_id'] to efficiently select the inhibitors and protein_ids from the related Gene table in the one SQL query, rather than doing multiple SQL sub-queries later)
    """
    error_msg = ""
    
    if gene_name == "":
        error_msg += 'Gene name is empty, but must be specified'
        return error_msg, None

    # Using driver_id=gene_name (or target_id=gene_name) avoids table join of (driver = gene):
    q = Dependency.objects.filter(driver_id=gene_name) if is_search_by_driver(search_by) else Dependency.objects.filter(target_id=gene_name)
        
    # As Query Sets are lazy, so can incrementally build the query, then it is evaluated once at end when it is needed:
    if histotype_name != "ALL_HISTOTYPES":
        q = q.filter( histotype = histotype_name ) # Correctly uses: =histotype_name, not: =histotype_full_name

    if study_pmid != "ALL_STUDIES":
        q = q.filter( study_id = study_pmid )  # Could use: (study = study) but using study_id should be more efficiewnt as no table join needed.

    q = q.filter(wilcox_p__lte = wilcox_p) # Only list significant hits (ie: p<=0.05). '__lte' means 'less than or equal to'

    if select_related is not None: 
        if isinstance(select_related, str) and select_related != '':
            q = q.select_related(select_related)
        elif isinstance(select_related, list) or isinstance(select_related, tuple):
            for column in select_related:
                q = q.select_related(column)
        else:
            error_msg += " ERROR: *** Invalid type for 'select_related' %s ***" %(type(select_related))
            print(error_msg)
     
    if order_by != None and order_by != '':
        q = q.order_by(order_by)  # usually 'wilcox_p', but could be: order_by('target_id') to order by target gene name
        
    return error_msg, q
    
    

def gene_ids_as_dictionary(gene):
    """ To return info about alternative gene Ids as dictionary, for an JSON object for AJAX """
    return {
        'gene_name': gene.gene_name,
        'entrez_id': gene.entrez_id,
        'ensembl_id': gene.ensembl_id,
        'ensembl_protein_id': gene.ensembl_protein_id,
        'vega_id': gene.vega_id,
        'omim_id': gene.omim_id,
        'hgnc_id': gene.hgnc_id,
        'cosmic_id': gene.cosmic_id,
        'uniprot_id': gene.uniprot_id
        }

def gene_info_as_dictionary(gene):
    """ To return info about the gene as a JSON object for AJAX """
    return {    
        'gene_name': gene.gene_name,
        'full_name': gene.full_name,
        'synonyms': gene.prevname_synonyms,
        'ids': gene_ids_as_dictionary(gene),
        }
    
    
def get_dependencies(request, search_by, gene_name, histotype_name, study_pmid):
    """ Fetches the dependency data from cache (if recent same query) or database, for the main search result webpage.
    After "Search" button on the "index.html" page is pressed an AJAX requst sends four fields: search_by, gene_name, histotype, and study_pmid.
    For paginated table, could add [start_row, and number_of_rows to return]
    Returns JSON formatted data for the dependency search result table, or an error message in JSON format.
    GET request is faster than POST, as POST makes two http requests, GET makes one, the Django url parameters are a GET request.
    """
    
    timing_array = []  # Using an array to preserve order of times on output.
    start = datetime.now()
    
    ajax_results_cache_version = '1' # version of the data in the database and of this JSON format. Increment this on updates that change the database data or this JSON format. See: https://docs.djangoproject.com/en/1.9/topics/cache/#cache-versioning
    
    # Avoid storing a 'None' value in the cache as then difficult to know if was a cache miss or is value of the key
    cache_key = search_by+'_'+gene_name+'_'+histotype_name+'_'+study_pmid+'_v'+ajax_results_cache_version
    cache_data = cache.get(cache_key, 'not_found') # To avoid returning None for a cache miss.
    if cache_data != 'not_found': 
        # start = get_timing(start, 'Retrieved from cache', timing_array)
        # The 'timings': timing_array in the cached version is saved from the actual previous query execution, is not the timing for retrieving from the cache.
        return HttpResponse(cache_data, json_mimetype) # version=ajax_results_cache_version)

    search_by_driver = is_search_by_driver(search_by) # otherwise is by target

    # Specify 'select_related' columns on related tables, otherwise the template will do a separate SQL query for every dependency row to retrieve the driver/target data (ie. hundreds of SQL queries on the Gene table)
    # Can add more select_related columns if needed, eg: for target gene prevname_synonyms: target__prevname_synonyms
    select_related = [ 'target__inhibitors', 'target__ensembl_protein_id' ] if search_by_driver else [ 'driver__inhibitors', 'driver__ensembl_protein_id' ]
    
    error_msg, dependency_list = build_dependency_query(search_by,gene_name, histotype_name, study_pmid, order_by='wilcox_p', select_related=select_related) 
    if error_msg != '': return json_error("Error: "+error_msg)
    
    gene = get_gene(gene_name)
    if gene is None: return json_error("Error: Gene '%s' NOT found in Gene table" %(gene_name))

    # Only need current_url to include it in title/browser tab on hoover, for testing.
    #current_url =  request.META['HTTP_HOST']  # or: request.META['SERVER_NAME']

    start = get_timing(start, 'Query setup', timing_array)
        
    results = []
    csv = ''
    div = ';' # Using semicolon as the div, as comma may be used to separate the inhibitors
    count = 0
    
    # "The 'iterator()' method ensures only a few rows are fetched from the database at a time, saving memory, but aren't cached if needed again in this function. This iteractor version seems slightly faster than non-iterator version.
    for d in dependency_list.iterator():
        count += 1

        interaction = d.interaction
        if interaction is None: interaction = ''  # shouldn't be None, as set by ' add_ensembl_proteinids_and_stringdb.py' script to ''.
        
        interation_protein_id = d.target.ensembl_protein_id if search_by_driver else d.driver.ensembl_protein_id
        if interation_protein_id is None: interation_protein_id = ''  # The ensembl_protein_id might be empty.
        interaction += '#'+interation_protein_id  # Append the protein id so can use this to link to string-db.org

        inhibitors = d.target.inhibitors if search_by_driver else d.driver.inhibitors
        if inhibitors is None: inhibitors = '' # shouldn't be None, as set by 'drug_inhibitors.py' script to ''.
        
        # For driver or target below, the '_id' suffix gets the underlying gene name, rather than the foreign key Gene object, so more efficient as no SQL join needed.
        # Similarily 'study_id' returns the underlying pmid number from Dependency table rather than the Study object.
        # wilcox_p in scientific format with no decimal places (.0 precision), and remove python's leading zero from the exponent.
        results.append([
                    d.target_id if search_by_driver else d.driver_id,
                    format(d.wilcox_p, ".0e").replace("e-0", "e-"),
                    format(d.effect_size*100, ".1f"),  # As a percentage with 1 decimal place
                    format(d.zdiff,".2f"), # Usually negative. two decomal places
                    d.histotype,
                    d.study_id,
                    interaction,
                    inhibitors # Formatted above
                    ])

    start = get_timing(start, 'Dependency results', timing_array)
    
    # results_column_names = ['Target','Wilcox_p','Effect_size','ZDiff','Histotype','Study_pmid','Inhibitors','Interactions'] # Could add this to the returned 'query_info'

    query_info = {'search_by': search_by,
                  'gene_name': gene_name,
                  'gene_full_name': gene.full_name,
                  'gene_synonyms': gene.prevname_synonyms,
                  'histotype_name': histotype_name,
                  'study_pmid': study_pmid,
                  'dependency_count': count, # should be same as: dependency_list.count(), but dependency_list.count() could be another SQL query. # should be same as number of elements passed in the results array.
                  }
                  # 'current_url': current_url # No longer needed.
                
    data = json.dumps({
        'success': True,
        'timings': timing_array,
        'query_info': query_info,
        'gene_ids': gene_ids_as_dictionary(gene),
        'results': results
        }, separators=[',',':']) # The default separators=[', ',': '] includes whitespace which I think make transfer to browser larger. As ensure_ascii is True by default, the non-asciii characters are encoded as \uXXXX sequences, alternatively can set ensure_ascii to false which will allow unicode I think.
    
    start = get_timing(start, 'Json dump', timing_array) # Although too late to add this time to the json already encoded above.

    cache.set(cache_key, data, version=ajax_results_cache_version) # could use the add() method instead, but better to update anyway.
    # Could gzip the cached data (using GZip middleware's gzip_page() decorator for the view, or in code https://docs.djangoproject.com/en/1.9/ref/middleware/#module-django.middleware.gzip )
    # GZipMiddleware will NOT compress content if any of the following are true:
    #  - The content body is less than 200 bytes long.
    #  - The response has already set the Content-Encoding header.
    #  - The request (the browser) hasn’t sent an Accept-Encoding header containing gzip.
    # Another option is using cache_control() permit browser caching by setting the Vary header: https://docs.djangoproject.com/en/1.9/topics/cache/#using-vary-headers
    # "(Note that the caching middleware already sets the cache header’s max-age with the value of the CACHE_MIDDLEWARE_SECONDS setting. If you use a custom max_age in a cache_control decorator, the decorator will take precedence, and the header values will be merged correctly.)"
    # https://www.pythonanywhere.com/forums/topic/376/
    # and example of gzip using flask: https://github.com/closeio/Flask-gzip
    #  https://github.com/closeio/Flask-gzip/blob/master/flask_gzip.py

    #print(timing_array) # To django console/server log
    return HttpResponse(data, content_type=json_mimetype) # As data is alraedy in json format, so not using JsonResponse(data, safe=False) which would try to convert it to JSON again.
    


def get_boxplot(request, dataformat, driver_name, target_name, histotype_name, study_pmid):
    """ Returns data for plotting the boxplots, in JSON or CSV format
    The 'target_variant' parameter is no longer used for the Achilles data, as only the target_variant with the best wilcox_p value is stored in the Dependency table """
    try:
        d = Dependency.objects.get(driver_id=driver_name, target_id=target_name, histotype=histotype_name, study_id=study_pmid)
        
    except ObjectDoesNotExist: # ie. not found by the objects.get()
        error_msg = "Error, Dependency: driver='%s' target='%s' tissue='%s' study='%s' NOT found in Dependency table" %(driver_name, target_name, histotype_name, study_pmid)
        if dataformat[:4] == 'json': # for request 'jsonplot' or 'jsonplotandgene'
          return json_error(error_msg)
        else:  
          return HttpResponse(error_msg, content_type=plain_mimetype)  # or could use csv_minetype
          
    if dataformat == 'csvplot':
        return HttpResponse(d.boxplot_data, content_type=csv_mimetype)

    if dataformat == 'jsonplot':
        return JsonResponse({'success': True, 'boxplot': d.boxplot_data}, safe=False)
   
    if dataformat == 'jsonplotandgene': # when browser doesn't already have target gene_info and ncbi_summary cached.
        try:
            gene = Gene.objects.get(gene_name=target_name)
            gene_info = gene_info_as_dictionary(gene);
            gene_info['ncbi_summary'] = gene.ncbi_summary  # To include the gene's ncbi_summary
            return JsonResponse( { 'success': True,
                                   'gene_info': gene_info,
                                   'boxplot': d.boxplot_data },
                                 safe=False )
        except ObjectDoesNotExist: # Not found by the objects.get()                    
            return json_error( "Error, Gene: target='%s' NOT found in Gene table" %(target_name) )

    elif dataformat=='csv' or dataformat=='download': 
        # 'csv' is for users to request the boxplot data via API
        # 'download' to for the 'Download as CSV' button on the SVG boxplots
        lines = d.boxplot_data.split(';')
        
        lines[0] = "Tissue,CellLine,Zscore,Altered";
        # This first line is the count, range, and boxplot_stats.
        
        # As this range and boxplot_stats are now calculated by the Javasscript in svg_boxplots.js, this line can be removed from future R output, so in future we need to prepend to the list, rather than replacing the first line here:
        #  lines.insert(0, "Tissue,CellLine,Zscore,Altered")
        # or just: 
        #  response = HttpResponse("Tissue,CellLine,Zscore,Altered\n" + (d.boxplot_data.replace(";","\n")), content_type=csv_mimetype)
        response = HttpResponse("\n".join(lines), content_type=csv_mimetype)
        if dataformat=='download':
            # Add to the HttpResponse object with the CSV/TSV header and downloaded filename:
            dest_filename = ('%s_%s_%s_pmid%s.csv' %(driver_name,target_name,histotype_name,study_pmid)).replace(' ','_') # To also replace any spaces with '_'
            # NOTE: Using .csv as Windows (and Mac) file associations will then know to open file with Excel, whereas if is .tsv then Windows won't open it with Excel.
            response['Content-Disposition'] = 'attachment; filename="%s"' %(dest_filename)
        return response
            
    else:
        print("*** Invalid dataformat requested for get_boxplot() ***")
        return HttpResponse("Error, Invalid dataformat '"+dataformat+"' requested for get_boxplot()", content_type=plain_mimetype)
        

        
    
def stringdb_interactions(required_score, protein_list):
    """ Retrieve list of protein_ids with interaction of >=required_score
         'required_score' is typically 400, or 700 (for 40% or 70% confidence)
         'protein_list' is ensembl protein_ids separated with semicolons ';'
    NOTE: The pythonanywhere.com free account blocks requests to servers not on their whitelist. String-db.org has now been added to their whitelist, so this function works ok on free or paid accounts.
    This function creates a request in format: http://string-db.org/api/psi-mi-tab/interactionsList?network_flavor=confidence&limit=0&required_score=700&identifiers=9606.ENSP00000269571%0D9606.ENSP00000357883%0D9606.ENSP00000345083
    """
    
    stringdb_options="network_flavor=confidence&limit=0&required_score="+required_score;    
    # The online interactive stringdb uses: "required_score" 400, and "limit" 0 (otherwise by default string-db will add 10 more proteins)
    # Optionally add parameter:  &additional_network_nodes=0
    
    protein_list = protein_list.replace(';', '%0D')  # Replace semicolon with the url encoded newline character,  which String-db expects between protein ids.

    url = "http://string-db.org/api/psi-mi-tab/interactionsList?"+stringdb_options+"&identifiers="+protein_list;
    
    # For very large result sets could use streaming: http://stackoverflow.com/questions/16870648/python-read-website-data-line-by-line-when-available
    # import requests
    # r = requests.get(url, stream=True)
    # for line in r.iter_lines():
    #   if line: print line

    req = Request(url)
    try:
        response = urlopen(req)
    except URLError as e:
        if hasattr(e, 'reason'):
            return False, 'We failed to reach a server: ' + e.reason
        elif hasattr(e, 'code'):
            return False, 'The server couldn\'t fulfill the request. Error code:' + e.code
    else:  # response is fine
        return True, response.read().decode('utf-8').rstrip().split("\n") # read() returns 'bytes' so need to convert to python string


def get_stringdb_interactions(request, required_score, protein_list=None):
    """ Returns the subset of protein protein_list that string-db reports have interactions with at least one other protein in the protein_list. This is to remove the unconnected proteins from the image """
    
    # The request can be optionally be sent by an HTML GET or POST. POST means no limit to number of proteins sent, whereas GET or Django url() params are limited by length of the URL the webbrowser permits.
    if (protein_list is None) or (protein_list == ''):
        protein_list = post_or_get_from_request(request,'protein_list')    
    
    # Fetch the subset of protein_list that  have actual interactions with other proteins in the list:
    success, response = stringdb_interactions(required_score, protein_list)

    if not success: return HttpResponse('ERROR: '+response, content_type=plain_mimetype)

    if response=='': return HttpResponse("", content_type=plain_mimetype) # No interacting proteins.
    # was: or response=="\n", but the newline in empty response is rstrip'ed in stringdb_interactions()
    
    # Dictionary to check later if returned protein was in original list:
    initial_protein_dict = dict((protein,True) for protein in protein_list.split(';'))
    
    err_msg = ''        
    final_protein_dict = dict()
    for line in response:
        if line == '': continue
        cols = line.rstrip().split("\t")
        if len(cols)<2: err_msg+="\nNum cols = %d (but expected >=2) in line: '%s'" %(len(cols),line.rstrip())
         
        for i in (0,1): # col[0] and col[1] are the pair of interacting proteins
            protein = cols[i].replace('string:', '') # as returned ids are prefixed with 'string:'
            if protein in initial_protein_dict: final_protein_dict[protein] = True
            else: err_msg+="\n*** Protein%d returned '%s' is not in original list ***" %(i+1,protein)
            
    if err_msg != '':
        print(err_msg)
        return HttpResponse('ERROR:'+err_msg, content_type=plain_mimetype)
            
    protein_list2 = ';'.join(final_protein_dict.keys())
    return HttpResponse(protein_list2, content_type=plain_mimetype)

    
    
def cytoscape(request, required_score, protein_list=None, gene_list=None):
    """ Displays the cytoscape network of protein interactions.
    This receives the protein_list and their corresponding gene_names as gene_list.
    Could just receive:
      - protein_list and lookup the corresponding gene_names in Gene table
      - gene_list and lookup the corresponding protein ids in the Gene table
      
    """
    if (protein_list is None) or (protein_list == ''):
        protein_list = post_or_get_from_request(request,'protein_list')

    if (gene_list is None) or (gene_list == ''):
        gene_list = post_or_get_from_request(request,'gene_list')
       
    success, response = stringdb_interactions(required_score, protein_list) # Fetches list of actual interactions
    
    if not success: return HttpResponse('ERROR: '+response, content_type=plain_mimetype)

    protein_list = protein_list.split(';')
    gene_list = gene_list.split(';')
    if len(protein_list) != len(gene_list):
        return HttpResponse('ERROR: lengths of gene_list and protein_list are different', content_type=plain_mimetype)

    # Create a dictionary to check later if returned protein was in original list, and what the gene_name was for that protein_id:            
    initial_nodes = dict()
    for i in range(0, len(protein_list)):
        initial_nodes[protein_list[i]] = gene_list[i]
    
    nodes = dict() # The protein nodes for cytoscape
    edges = dict() # The edges for cytoscape
    err_msg = ''
    for line in response:
      # if line:
        cols = line.rstrip().split("\t")
        if len(cols)<2: err_msg += "\nNum cols = %d (expected >=2) in line: '%s'" %(len(cols),line.rstrip())
        
        protein1 = cols[0].replace('string:', '') # as ids are prefixed with 'string:'
        if protein1 in initial_nodes:
            nodes[ protein1.replace('9606.', '') ] = True # remove the human tax id
        else: err_msg += "\n*** Protein1 returned as '%s' is not in original list ***" %(protein1)

        protein2 = cols[1].replace('string:', '')
        if protein2 in initial_nodes:
            nodes[ protein2.replace('9606.', '') ] = True
        else: err_msg += "\n*** Protein2 returned as '%s' is not in original list ***" %(protein2)

        edge = protein1+'#'+protein2
        edge_reversed = protein2+'#'+protein1
        if edge not in edges and edge_reversed not in edges:
            edges[edge] = True

    # node_list = sorted(nodes)

    # Convert node list of protein_ids, to list of gene_names:
    for protein in protein_list: # Can't use 'initial_nodes' here as it will be updated
        initial_nodes[protein.replace('9606.', '')] = initial_nodes.pop(protein)
        
    node_list = []
    for protein in nodes:
        node_list.append(initial_nodes[protein])
        
    edge_list = [] # Will be an array of tuples.
    for edge in edges:
        proteins = edge.split('#')
        if len(proteins) != 2:
            err_msg += "\n**** Expected two proteins in edge, but got: "+edge
        edge_list.append( ( initial_nodes[proteins[0]], initial_nodes[proteins[1]] ) )

    if err_msg != '':
        print(err_msg)
        return HttpResponse('ERROR:'+err_msg, content_type=plain_mimetype)
    
    context = {'node_list': node_list, 'edge_list': edge_list}
    return render(request, 'gendep/cytoscape.html', context)


    
def gene_info(request, gene_name):
    try:        
        data = gene_info_as_dictionary( Gene.objects.get(gene_name=gene_name) )
        data['success'] = True # Add success: True to the json response.
        return JsonResponse(data, safe=False)
        
    except ObjectDoesNotExist: # Not found by the objects.get()
        return json_error("Gene '%s' NOT found in Gene table" %(gene_name))

        
def show_study(request, study_pmid):
    requested_study = get_object_or_404(Study, pk=study_pmid)
    # requested_study = get_object_or_404(Study, pk='Pending001') # Temportary for now.
    return render(request, 'gendep/study.html', {'study': requested_study})

def about(request):
    return render(request, 'gendep/about.html')

def tutorial(request):
    return render(request, 'gendep/tutorial.html')
        
def drivers(request):
    driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
    context = {'driver_list': driver_list}
    return render(request, 'gendep/drivers.html', context)

def targets(request):
    target_list = Gene.objects.filter(is_target=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_target)
    context = {'target_list': target_list}
    return render(request, 'gendep/targets.html', context)
    
def tissues(request):
    histotype_list = Dependency.HISTOTYPE_CHOICES
    context = {'histotype_list': histotype_list}
    return render(request, 'gendep/tissues.html', context)
    
def studies(request):
    study_list = Study.objects.order_by('pmid')
    context = {'study_list': study_list}
    return render(request, 'gendep/studies.html', context)

def faq(request):
    current_url =  request.META['HTTP_HOST'] # See download_dependencies_as_csv_file() for other, maybe better, ways to obtain currrent_url
    context = {'current_url': current_url}
    return render(request, 'gendep/faq.html', context)
    
def contact(request):
    return render(request, 'gendep/contact.html')



search_by_driver_column_headings_for_download = ['Dependency', 'Dependency description', 'Entez_id',  'Ensembl_id', 'Ensembl_protein_id', 'Dependency synonyms', 'Wilcox P-value', 'Effect size', 'Z diff', 'Tissue', 'Inhibitors', 'String interaction', 'Study', 'PubMed Id', 'Experiment Type', 'Boxplot link']                                 
search_by_target_column_headings_for_download = ['Driver', 'Driver description', 'Entez_id',  'Ensembl_id', 'Ensembl_protein_id', 'Driver synonyms', 'Wilcox P-value', 'Effect size', 'Z diff', 'Tissue', 'Inhibitors', 'String interaction', 'Study', 'PubMed Id', 'Experiment Type', 'Boxplot link']


# ===========================================    
def download_dependencies_as_csv_file(request, search_by, gene_name, histotype_name, study_pmid, delim_type='csv'):
    """ Creates then downloads the current dependency result table as a tab-delimited file.
    The download get link needs to contain: serach_by, gene, tissue, study parameters.

    In Windows at least, 'csv' files are associated with Excel, so will be opened by Excel. 
    To also associate a '.tsv' file with excel: In your browser, create a helper preference associating file type 'text/tab-separated values' and file extensions 'tsv' with application 'Excel'. Pressing Download will then launch Excel with the '.tsv' data file.
    
    ***** Remember to add to the select_related lists below if other columns are required for output.
    """
    
    mimetype = html_mimetype # was: 'application/json'
    
    # see: http://stackoverflow.com/questions/6587393/resource-interpreted-as-document-but-transferred-with-mime-type-application-zip
    
    # For downloading large csv files, can use streaming: https://docs.djangoproject.com/en/1.9/howto/outputting-csv/#streaming-large-csv-files
    
    # request_method = request.method # 'POST' or 'GET'
    # if request_method != 'GET': return HttpResponse('Expected a GET request, but got a %s request' %(request_method), mimetype)
    # search_by = request.GET.get('search_by', "")  # It's an ajax POST request, rather than the usual ajax GET request
    # gene_name = request.GET.get('gene', "")
    # histotype_name = request.GET.get('histotype', "ALL_HISTOTYPES")
    # study_pmid = request.GET.get('study', "ALL_STUDIES")

    search_by_driver = is_search_by_driver(search_by) # Checks is valid and returns true if search_by='driver'
        
    # select_related = [ 'target__inhibitors', search_by, 'study' ] if search_by_driver else [ 'driver__inhibitors', search_by, 'study' ]   # Could add 'target__ensembl_protein_id' or 'driver__ensembl_protein_id'
    
    # But for a more precise query (and so faster as retrieves fewer columns) is:
    if search_by_driver:
        select_related = [ 'target__gene_name', 'target__full_name', 'target__entrez_id', 'target__ensembl_id', 'target__ensembl_protein_id', 'target__prevname_synonyms' ]
    else:
        select_related = [ 'driver__gene_name', 'driver__full_name', 'driver__entrez_id', 'driver__ensembl_id', 'driver__ensembl_protein_id', 'driver__prevname_synonyms' ]
    select_related.extend([ 'study__short_name', 'study__experiment_type', 'study__title' ]) # don't need 'study__pmid' (as is same as d.study_id)
    # *** Remember to add to these select_related lists if other columns are required for output.
                
    error_msg, dependency_list = build_dependency_query(search_by, gene_name, histotype_name, study_pmid, select_related=select_related, order_by='wilcox_p' ) # using 'select_related' will include all the Gene info for the target/driver in one SQL join query, rather than doing multiple subqueries later.
    
    if error_msg != '': return HttpResponse("Error: "+error_msg, mimetype)

    histotype_full_name = get_histotype_full_name(histotype_name)
    if histotype_full_name is None: return HttpResponse("Error: Tissue '%s' NOT found in histotype list" %(histotype_name))
    
    study = get_study(study_pmid)
    if study is None: return HttpResponse("Error: Study pmid='%s' NOT found in Study table" %(study_pmid))

    # Retrieve the host domain for use in the boxplot file links:
    # current_url =  request.META['HTTP_HOST']

    # Set the deliminators
    #   Another alternative would be: csv.unix_dialect
    #   csv.excel_tab doesn't display well.
    if delim_type=='csv':
        dialect = csv.excel
        content_type = csv_mimetype # can be called: 'application/x-csv' or 'application/csv'
    elif delim_type=='tsv':
        dialect = csv.excel_tab
        content_type = tab_mimetype
    elif delim_type=='xlsx':   # A real Excel file.
        content_type = excel_minetype
    else:
        return HttpResponse("Error: Invalid delim_type='%s', as must be 'csv' or 'tsv' or 'xlsx'"%(delim_type), mimetype)

    timestamp = time.strftime("%d-%b-%Y") # To add time use: "%H:%M:%S")

    dest_filename = ('dependency_%s_%s_%s_%s_%s.%s' %(search_by,gene_name,histotype_name,study_pmid,timestamp,delim_type)).replace(' ','_') # To also replace any spaces with '_' 
    # NOTE: Is '.csv' so that Windows will then know to open Excel, whereas if is '.tsv' then won't.

    # Create the HttpResponse object with the CSV/TSV header and downloaded filename:
    response = HttpResponse(content_type=content_type) # Maybe use the  type for tsv files?    
    response['Content-Disposition'] = 'attachment; filename="%s"' %(dest_filename)

    count = dependency_list.count()
    study_name = "All studies" if study_pmid=='ALL_STUDIES' else study.short_name
    file_description = "A total of %d dependencies were found for: %s='%s', Tissue='%s', Study='%s'" % (count, search_by.title(), gene_name, histotype_full_name, study_name)
    file_download_text = "Downloaded from cancergd.org on %s" %(timestamp)
    
    column_headings = search_by_driver_column_headings_for_download if search_by_driver else search_by_target_column_headings_for_download
    
    if delim_type=='csv' or delim_type=='tsv':
        writer = csv.writer(response, dialect=dialect)
        # Maybe: newline='', Can add:  quoting=csv.QUOTE_MINIMAL, or csv.QUOTE_NONE,  Dialect.delimiter,  Dialect.lineterminator
            
        writer.writerows([
            ["",file_description,], # Added extra first column so Excel knows from first row that is CSV
            ["",file_download_text,],
            ["",],
          ]) # Note needs the comma inside each square bracket to make python interpret each line as list than that string

        writer.writerow(column_headings)
           # The writeheader() with 'fieldnames=' parameter is only for the DictWriter object.         

    elif delim_type=='xlsx': # Real excel file
        import xlsxwriter # need to install this 'xlsxwriter' python module

        # An advantage of Excel format is if import tsv file Excel changes eg. MARCH10 or SEP4 to a date, whereas creating the Excle file doesn't
        # Also can add formatting, better url links, and include box-plot images.
        #import io            
        #iobytes_output = io.BytesIO() # Workbook expects a string or bytes object, and cannot write it directly to response.
        #workbook = xlsxwriter.Workbook(iobytes_output, {'in_memory': True})
        workbook = xlsxwriter.Workbook(response)
        # As output is small, {'in_memory': True} avoids using temp files on server
        # or: with xlsxwriter.Workbook(iobytes_output, {'in_memory': True}) as workbook: (then don't need to close() it)
        
        workbook.set_properties({
          'title':    file_description,
          'subject':  'Cancer Genetic Dependencies',
          'author':   'CancerGD.org',
          'manager':  'Dr. Colm Ryan',
          'company':  'Systems Biology Ireland',
          'category': '',
          'keywords': 'Sample, Example, Properties',
          'comments': 'Created with Python and XlsxWriter. '+file_download_text,
          'status': '',
          'hyperlink_base': '',
          })
        
        ws = workbook.add_worksheet() # can have optional sheet_name parameter
        yellow = '#FFFFEE' # a light yellow
        bold = workbook.add_format({'bold': True}) # Add a bold format to use to highlight cells.
        # bold_cyan = workbook.add_format({'bold': True, 'bg_color': 'cyan'}) # Add a bold blue format.
        # bold_yellow = workbook.add_format({'bold': True, 'bg_color': yellow}) # Add a bold blue format.
        # bg_yellow = workbook.add_format({'bg_color': yellow})
        # But when use background colour then hides the vertical grid lines that separate the cells
        align_center = workbook.add_format({'align':'center'})
        exponent_format = workbook.add_format({'num_format': '0.00E+00', 'align':'center'}) # For wilcox_p (eg 1 x 10^-4).
        percent_format = workbook.add_format({'num_format': '0.00"%"', 'align':'center'}) # For effect_size.
        two_decimal_places = workbook.add_format({'num_format': '0.00', 'align':'center'}) # For Z-diff.

        
        # can also set border formats using:    set_bottom(), set_top(), set_left(), set_right()
        # also can set cell bg colours (eg: 'bg_color'), etc http://xlsxwriter.readthedocs.org/format.html

        ws.write_string( 1, 1, file_description )
        ws.write_string( 2, 1, file_download_text )
        ws.write_row   ( 4, 0, column_headings, bold)
        #  ws.set_row(row, None, bold) # To make title row bold - but already set to bold above in write_row
        ws.set_column(0, 0, 12) # To make Gene name column (col 0) a bit wider
        ws.set_column(1, 1, 35) # To make Description column (col 1) wider
        ws.set_column(3, 4, 16) # To make ensembl ids (col 3 and 4) wider
        ws.set_column(5, 5, 35) # To make Synonyms column (col 5) wider
        ws.set_column(6, 13, 11) # To make columns 6 to 13 a bit wider
        ws.set_column(14, 14, 14) # To make Experiment_type (col 14) a bit wider
        row = 4 # The last row to writen
        
    # Now write the dependency rows:
    for d in dependency_list:  # Not using iteractor() as count() above will already have run the query, so is cached

        # If could use 'target AS gene' or 'driver AS gene' in the django query then would need only one output:
        if search_by_driver:
            # Cannot use 'gene_id' as variable, as that will refer to the primary key of the Gene table, so returns a tuple.
            gene_symbol= d.target.gene_name # d.target_id but returns name as a tuple, # same as: d.target.gene_name
            full_name  = d.target.full_name
            entrez_id  = d.target.entrez_id
            ensembl_id = d.target.ensembl_id
            protein_id = d.target.ensembl_protein_id
            synonyms   = d.target.prevname_synonyms
            inhibitors = d.target.inhibitors
        else:  # search_by target
            gene_symbol= d.driver.gene_name # d.driver_id, # same as: d.driver.gene_name
            full_name  = d.driver.full_name
            entrez_id  = d.driver.entrez_id
            ensembl_id = d.driver.ensembl_id
            protein_id = d.driver.ensembl_protein_id
            synonyms   = d.driver.prevname_synonyms
            inhibitors = d.driver.inhibitors
        #print(gene_symbol, d.target.gene_name)

        if delim_type=='csv' or delim_type=='tsv':
            writer.writerow([
                gene_symbol,
                full_name, entrez_id, ensembl_id, protein_id, synonyms,
                format(d.wilcox_p, ".1e").replace("e-0", "e-"),
                format(d.effect_size*100, ".1f"),  # As a percentage with 1 decimal place
                format(d.zdiff,".2f"), # Usually negative
                d.get_histotype_display(),
                inhibitors,
                d.interaction,
                d.study.short_name,  d.study_id,  d.study.experiment_type
                ])
                # d.study_id is same as 'd.study.pmid'
        
            # Could add weblinks to display the SVG boxplots by pasting link into webbrowser:
            # this 'current_url' is a temporary fix: (or use: StaticFileStorage.url )
            # 'http://'+current_url+'/static/gendep/boxplots/'+d.boxplot_filename()
            
        elif delim_type=='xlsx':
            row += 1
            ws.write_string(row,   0, gene_symbol, bold)
            ws.write_string(row,   1, full_name)
            ws.write_string(row,   2, entrez_id)
            ws.write_string(row,   3, ensembl_id)
            ws.write_string(row,   4, protein_id)
            ws.write_string(row,   5, synonyms)
            ws.write_number(row,   6, d.wilcox_p,    exponent_format)
            ws.write_number(row,   7, d.effect_size, percent_format)
            ws.write_number(row,   8, d.zdiff,       two_decimal_places)
            ws.write_string(row,   9, d.get_histotype_display())
            ws.write_string(row,  10, inhibitors)
            ws.write_string(row,  11, d.interaction, align_center)
            ws.write_string(row,  12, d.study.short_name)
            ws.write_url(   row,  13, url=d.study.url(), string=d.study_id, tip='PubmedId: '+d.study_id+' : '+d.study.title)  # cell_format=bg_yellow  # d.study_id is same as 'd.study.pmid'
            ws.write_string(row,  14, d.study.experiment_type)
            # ws.write_string(row, 15, d.study.summary)
        
            # ADD THE FULL STATIC PATH TO THE url = .... BELOW:
            # ws.write_url(   row, 14, url = 'gendep/boxplots/'+d.boxplot_filename, string=d.boxplot_filename, tip='Boxplot image')
            # ws.insert_image(row, col, STATIC.....+d.boxplot_filename [, options]) # Optionally add the box-plots to excel file.

    # Close the Excel file
    if delim_type=='xlsx':
        workbook.close() # must close to save the contents.
        # xlsx_data = output.getvalue()
        # response.write(iobytes_output.getvalue())    # maybe add: mimetype='application/ms-excel'
        # or:
        # output.seek(0)
        # response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    return response
    
