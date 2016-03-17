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


 
def index(request, driver=''): # Default is search boxes, with driver dropdown populated with driver gene_names (plus an empty name).
    driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
    # histotype_list = Histotype.objects.order_by('full_name')
    histotype_list = Dependency.HISTOTYPE_CHOICES
    study_list = Study.objects.order_by('pmid')
    dependency_list = None # For now.
    
    # This page can be called from the 'drivers' page, with a driver as a POST parameter, so then should display the POST results?
    if driver == '': # if driver not passed using the '/driver_name' parameter in urls.py
        if   request.method == 'GET':  driver = request.GET.get('driver', '')
        elif request.method == 'POST': driver = request.POST.get('driver', '')
        else: driver = ''
    
    # current_url = request.get_full_path() # To display the host in title for developing on lcalhost or pythonanywhere server.
    # current_url = request.build_absolute_uri()
    #current_url =  request.META['SERVER_NAME']
    current_url =  request.META['HTTP_HOST']

    # Optionally could add locals() to the context to pass all local variables, eg: return render(request, 'app/page.html', locals())
    context = {'driver': driver, 'driver_list': driver_list, 'histotype_list': histotype_list, 'study_list': study_list, 'dependency_list': dependency_list, 'current_url': current_url}
    return render(request, 'gendep/index.html', context)


def get_drivers(request):
    # View for the driver_jquery search box.
    if request.is_ajax():
        q = request.GET.get('term', '')  #  jQuery autocomplete sends the query as "term" and it expects back three fields: id, label, and value. It will use those to display the label and then the value to autocomplete each driver gene.
        # driver_list = Gene.objects.filter(is_driver=True).order_by('gene_name')  # Needs: (is_driver=True), not just: (is_driver)
        drivers = Gene.objects.filter(is_driver=True, gene_name__icontains = q)   # [:20]
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


def build_dependency_query(driver_name, histotype_name, study_pmid, wilcox_p=0.05):
    error_msg = ""
    
    if driver_name == "":
        error_msg = 'Driver name is empty, but must be specified'
        return error_msg, None, None, None, None

    # As Query Sets are lazy, so can build query and evaluated once at end:
    q = Dependency.objects.filter(wilcox_p__lte = wilcox_p) # Only list significant hits (ie: p<=0.05)
        
    try:
        driver = Gene.objects.get(gene_name=driver_name)
        # driver = None if driver_name == '' else Gene.objects.get(gene_name=driver_name)
        q = q.filter( driver = driver )  # q = q.filter( driver__gene_name = driver )
    except ObjectDoesNotExist: # Not found by the objects.get()
        error_msg = "Driver '%s' NOT found in Gene table" %(driver_name)  # if driver is None
        return error_msg, None, None, None, None

    if histotype_name != "ALL_HISTOTYPES":
        histotype_full_name = Dependency.histotype_full_name(histotype_name)
        q = q.filter( histotype = histotype_name ) # This correctly uses "...= histotype_name" (not "...= histotype_full_name")
    else: 
        histotype_full_name = "All tissues"

    if study_pmid != "ALL_STUDIES":
        try:
            study = Study.objects.get(pmid=study_pmid)
            q = q.filter( study = study )
        except ObjectDoesNotExist: # Not found by the objects.get()
            error_msg = "Study pmid='%s' NOT found in Study table" %(study_pmid)
            return error_msg, None, None, None, None
    else:
        study = "ALL_STUDIES"
    
    return error_msg, q, driver, histotype_full_name, study
    
    
def ajax_results(request):
    # View for the dependency search result table.
    # Ajax sends four fields: driver, histotype, pmid, [start(row for pagination):
    mimetype = 'text/html' # was: 'application/json'
    request_method = request.method # 'POST' or 'GET'
    if request_method != 'POST': return HttpResponse('Expected a POST request, but got a %s request' %(request_method), mimetype)

    if not request.is_ajax(): return HttpResponse('fail', mimetype)

    driver_name = request.POST.get('driver', "")  # It's an ajax POST request, rather than the usual ajax GET request
    histotype_name = request.POST.get('histotype', "ALL_HISTOTYPES")
    study_pmid = request.POST.get('study', "ALL_STUDIES")

    error_msg, query, driver, histotype_full_name, study = build_dependency_query(driver_name, histotype_name, study_pmid)
    if error_msg != '': return HttpResponse("Error: "+error_msg, mimetype)

    dependency_list = query.order_by('wilcox_p')  # was: order_by('target__gene_name')

    gene_weblinks = driver.external_links('|')
       
    current_url =  request.META['HTTP_HOST']  # or: request.META['SERVER_NAME']

    context = {'dependency_list': dependency_list, 'driver': driver, 'histotype': histotype_name, 'histotype_full_name': histotype_full_name, 'study': study, 'gene_weblinks': gene_weblinks, 'current_url': current_url}
    return render(request, 'gendep/ajax_results.html', context, content_type=mimetype) #  ??? .. charset=utf-8"



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
    return render(request, 'gendep/drivers.html', context)

def studies(request):
    study_list = Study.objects.order_by('pmid')
    context = {'study_list': study_list}
    return render(request, 'gendep/studies.html', context)

def contact(request):
    return render(request, 'gendep/contact.html')


column_headings_for_download = ['Dependency', 'Dependency description', 'Entez_id',  'Ensembl_id', 'Dependency synonyms', 'Wilcox P-value', 'Effect size', 'Tissue', 'Inhibitors', 'Known interaction', 'Study', 'PubMed Id', 'Experiment Type', 'Boxplot link']
    
# ===========================================    
def download_dependencies_as_csv_file(request, driver_name, histotype_name, study_pmid, delim_type='csv'):
    # Creates then downloads the current dependency result table as a tab-delimited file.
    # The download get link needs to contain driver, tissue, study parameters.

    # In Windows at least, 'csv' files are associated with Excel. To also associate tsv file with excel: In your browser, create a helper preference associating file type 'text/tab-separated values' and file extensions 'tsv' with application 'Excel'. Pressing Download will then launch Excel with the data.
    import csv, time
    
    mimetype = 'text/html' # was: 'application/json'
    
    # For downloading large csv files, can use streaming: https://docs.djangoproject.com/en/1.9/howto/outputting-csv/#streaming-large-csv-files
    
    # request_method = request.method # 'POST' or 'GET'
    # if request_method != 'GET': return HttpResponse('Expected a GET request, but got a %s request' %(request_method), mimetype)
    # driver_name = request.GET.get('driver', "")  # It's an ajax POST request, rather than the usual ajax GET request
    # histotype_name = request.GET.get('histotype', "ALL_HISTOTYPES")
    # study_pmid = request.GET.get('study', "ALL_STUDIES")

    error_msg, query, driver, histotype_full_name, study = build_dependency_query(driver_name, histotype_name, study_pmid)
    if error_msg != '': return HttpResponse("Error: "+error_msg, mimetype)

    dependency_list = query.order_by('wilcox_p')  # was: order_by('target__gene_name')

    #gene_weblinks = driver.external_links('|')
    
    # was: study__pmid=request.POST.get('study')
    # [:20] use: 'target__gene_name' instead of 'target.gene_name'
    # dependency_list_count = dependency_list.count()+1

    timestamp = time.strftime("%d-%b-%Y") # To add time use: "%H:%M:%S")

    dest_filename = ('dependency_%s_%s_%s_%s.csv' %(driver_name,histotype_name,study_pmid,timestamp)).replace(' ','_') # To also replace any spaces with '_' NOTE: Is .csv as Windows will then know to open Excel, whereas if is tsv then won't

    # current_url = request.get_full_path() # To display the host in title for developing on lcalhost or pythonanywhere server.
    # current_url = request.build_absolute_uri()
    #current_url =  request.META['SERVER_NAME']
    current_url =  request.META['HTTP_HOST']
    
    # Or better method: http://stackoverflow.com/questions/17866114/django-get-absolute-url
    # from django.core.urlresolvers import reverse
    # url = request.build_absolute_uri(reverse('blog:detail', args=[blog.slug]))
    # BUT I want the static url...
    
    # Maybe use:  StaticFileStorage.url which effectively just prepends STATIC_URL to the path given,
    # but in more complex setups (eg. on S3) it does more.  ..... Another great example of when you absolutely must use the static tag: if you’re using Django’s CachedStaticFilesStorage as described in my post about Setting up static file caching, because it uses a hash of the file’s contents as part of the file name (so css/styles.css might be saved as css/styles.55e7cbb9ba48.css) and no amount of carefully constructing STATIC_URL will help you here!
    # from http://staticfiles.productiondjango.com/blog/stop-using-static-url-in-templates/
    # Setting up staic file caching: http://staticfiles.productiondjango.com/blog/setting-up-static-file-caching/
    
    
    # or create and register a 'absurl' tag for templates, which uses the above function ...
    #or request.get_host() but might not work if site behind proxy 
    # From: https://docs.djangoproject.com/en/1.9/howto/outputting-csv/
    # Using the Sites framework might be better: https://docs.djangoproject.com/en/dev/ref/contrib/sites/#how-django-uses-the-sites-framework
    # Simplest method is just to set the static url accordingly in the settings file: http://stackoverflow.com/questions/16573324/using-relative-vs-absolute-url-for-static-url-in-django
    # set DEVELOPMENT to True or False, then:
    # if DEVELOPMENT == True: STATIC_URL = '/static/'
    # else: STATIC_URL = 'https://www.mywebsite.com/static/'

    if delim_type=='csv':
        dialect = csv.excel
        content_type='text/csv'
    elif delim_type=='tsv':
        dialect = csv.excel_tab
        content_type='text/tab-separated-values'
    else:
        return HttpResponse("Error: Invalid delim_type='%s', as must be 'csv' or 'tsv'"%(delim_type), mimetype)

    # Create the HttpResponse object with the CSV/TSV header and downloaded filename:
    response = HttpResponse(content_type=content_type) # Maybe use the  type for tsv files?
    response['Content-Disposition'] = 'attachment; filename="%s"' %(dest_filename)
    
    writer = csv.writer(response, dialect=dialect)  # An alternative would be: csv.unix_dialect
    # csv.excel_tab doesn't display well
    # Maybe: newline='', Can add:  quoting=csv.QUOTE_MINIMAL, or csv.QUOTE_NONE,  Dialect.delimiter,  Dialect.lineterminator
    
    writer.writerow(column_headings_for_download) # The writeheader() with 'fieldnames=' parameter is only for the DictWriter object. headings are: ['Dependency', 'Dependency description', 'Entez_id',  'Ensembl_id', 'Dependency synonyms', 'Wilcox P-value', 'Effect size', 'Tissue', 'Inhibitors', 'Known interaction', 'Study', 'PubMed Id', 'Experiment Type', 'Box plot']

    count = 0  # or use: query.count()
    for d in dependency_list:
        count+=1
        writer.writerow([
            d.target.gene_name,
            d.target.full_name,
            d.target.entrez_id,
            d.target.ensembl_id,
            d.target.prev_names_and_synonyms_spaced(),
            d.wilcox_p,    # |stringformat:".0E",  # was, d.wilcox_p_power10_format  but <sup>-4</sup> not that meaningful in excel
  		    d.effect_size,
            d.get_histotype_display(),
            '', # d.inhibitors,
            '', # d.interaction,
            d.study.short_name,
            d.study.pmid,
            d.study.experiment_type,
            # d.study.summary,
            # ADD THE FULL STATIC PATH TO THE url = .... BELOW, this 'current_url' is a temporary fix: (or use: StaticFileStorage.url )
            current_url+'/static/gendep/boxplots/'+d.boxplot_filename()   # Using the full url path so can paste into browser.
            ])

    study_name = "All studies" if study_pmid=='ALL_STUDIES' else study.short_name
    writer.writerows([
        '',
        'A total of %d dependicies found for: Driver="%s", Tissue="%s", Study="%s"' % (count, driver_name,histotype_full_name, study_name),
        'Downloaded from CGDD on %s' %(timestamp)
        ])
            
    return response
    



#dialect = csv.Sniffer().sniff(csvfile.read(1024))
#    csvfile.seek(0)
#    reader = csv.reader(csvfile, dialect)
#    The excel_tab class defines the usual properties of an Excel-generated TAB-delimited file. It is registered with the dialect name 'excel-tab'.

#Dialect.delimiter    A one-character string used to separate fields. It defaults to ','.





"""
*** Finish this: download_dependencies_as_excel_file
### An advantage of Excel format is if import tsv file Excel changes eg. MARCH10 or SEP4 to a date, whereas creating the Excle fiile doesn't
# Also can add formatting, better url links, and include box-plot images.

def show_excel(request):
   # use a StringIO buffer rather than opening a file
   output = StringIO()
   w = csv.writer(output)
   for i in range(10):
      w.writerow(range(10))
   # rewind the virtual file
   output.seek(0)
   return HttpResponse(output.read(),
      )
  
  
def download_dependencies_as_excel_file(request):
    ## **** GOOD example: http://assist-software.net/blog/how-export-excel-files-python-django-application
    # http://www.developer.com/tech/article.php/10923_3727616_2/Creating-Excel-Files-with-Python-and-Django.htm
    import xlsxwriter  # need to install this python module
    # http://xlsxwriter.readthedocs.org/en/latest/index.html
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xlsx' %(filename)
    # xlsx_data = WriteToExcel(weather_period, town)
    # using xlsxwriter: http://xlsxwriter.readthedocs.org/worksheet.html

    # Another good alternaive is OpenPyXL: https://openpyxl.readthedocs.org/en/2.5/tutorial.html
    # eg: http://djangotricks.blogspot.co.uk/2013/12/how-to-export-data-as-excel.html
    # "Office Open XML Format - XLSX (a.k.a. OOXML or OpenXML) is a zipped, XML-based file format developed by Microsoft. It is fully supported by Microsoft Office 2007 and newer versions....
    
    # In python can add short descriptions to functions I think, eg: export_xlsx.short_description = u"Export XLSX"
    
    # or pyExcelerator: http://www.developer.com/tech/article.php/10923_3727616_2/Creating-Excel-Files-with-Python-and-Django.htm
    #  https://sourceforge.net/projects/pyexcelerator/ but last update is 2013
    # As well as setting content_type, should this function (but probably is same effect):  return HttpResponse(output.read(), mimetype='application/ms-excel')
    - answer is in Django >= 1.5 use content_type :
    import io

from django.http.response import HttpResponse

from xlsxwriter.workbook import Workbook


def your_view(request):

    output = io.BytesIO()

    workbook = Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, 'Hello, world!')
    workbook.close()

    output.seek(0)

    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=test.xlsx"

    return response
    
    
    
    # or xlwt: https://pypi.python.org/pypi/xlwt  eg: http://stackoverflow.com/questions/20040965/how-to-export-data-in-python-with-excel-format
    # Create an new Excel file and add a worksheet.
    # workbook = xlsxwriter.Workbook('demo.xlsx')
    
    ### **** GOOD Example:  http://xlsxwriter.readthedocs.org/example_http_server3.html?highlight=django
    output = StringIO()
    maybe use BytesIO in Python 3??? - Most uses of StringIO need to be migrated to BytesIO, when used as a byte buffer. If used as a string buffer, the StringIO uses need to be left at StringIO. http://dafoster.net/articles/2013/04/09/making-an-existing-python-program-unicode-aware/
    
    **** GOOD: http://stackoverflow.com/questions/16393242/xlsxwriter-object-save-as-http-response-to-create-download-in-django
    
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(optional_sheet_name)

    worksheet.write('A1', 'Hello')
    workbook.close() # is needed.

    xlsx_data = output.getvalue()
   workbook.set_properties({
    'title':    'This is an example spreadsheet',
    'subject':  'With document properties',
    'author':   'John McNamara',
    'manager':  'Dr. Heinz Doofenshmirtz',
    'company':  'of Wolves',
    'category': 'Example spreadsheets',
    'keywords': 'Sample, Example, Properties',
    'comments': 'Created with Python and XlsxWriter'}) 
... also: 'status':
     'hyperlink_base':
    set_properties() - Set the document properties such as Title, Author etc.
    # see: http://xlsxwriter.readthedocs.org/workbook.html
    
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)  # as is small files, to avoid using temp files, maybe use: {'in_memory': True}
...
...
    workbook.close()    
    
 or if use with, then doesn't need close:
 with xlsxwriter.Workbook('hello_world.xlsx') as workbook:
    worksheet = workbook.add_worksheet()

 
   worksheet.write('A1', 'Hello world')
 
    # Here we will adding the code to add data
 

    xlsx_data = output.getvalue()
    
    or 
    worksheet = workbook.add_worksheet()
    
    bold = workbook.add_format({'bold': 1}) # Add a bold format to use to highlight cells.
    exponent_format = workbook.add_format({'num_format': '0.00E+00'})     # Add a number format for cells with, eg 1 x 10-4.
    
    # also can set cell colours (eg: 'bg_color') and borders, etc http://xlsxwriter.readthedocs.org/format.html

    row = 0
    ws.write_row(row, 0 column_headings_for_download, bold)
    # ['Dependency', 'Dependency description', 'Entez_id',  'Ensembl_id', 'Dependency synonyms', 'Wilcox P-value', 'Effect size', 'Tissue', 'Inhibitors', 'Known interaction', 'Study', 'PubMed Id', 'Experiment Type', 'Experiment summary']
    # ws.set_row(0, None, bold) # To make title row bold
    ws.set_column(1, 1, 20) # To make Description column (col 1) wider
    ws.set_column(4, 4, 20) # To make Synonyms column (col 1) wider

    for d in dependency_list:
        row += 1
        ws.write_string(row,  0, d.target.gene_name, bold)
        ws.write_string(row,  1, d.target.full_name)
        ws.write_string(row,  2, d.target.entrez_id)
        ws.write_string(row,  3, d.target.ensembl_id)
        ws.write_string(row,  4, d.target.prev_names_and_synonyms_spaced)
        ws.write_number(row,  5, d.wilcox_p, exponent_format)  # |stringformat:".0E",  # was, d.wilcox_p_power10_format  but <sup>-4</sup> not that meaningful in excel
  	    ws.write_number(row,  6, d.effect_size)
        ws.write_string(row,  7, d.get_histotype_display)
        ws.write_string(row,  8, d.inhibitors)
        ws.write_boolean(row, 9, d.interaction)
        ws.write_string(row, 10, d.study.short_name)
        ws.write_url(   row, 11, url=d.study.url, string=d.study.pmid, tip='PubmedId: '+d.study.pmid+' : '+d.study.title)
        ws.write_string(row, 12, d.study.experiment_type)
        # ws.write_string(row, 13, d.study.summary)
        
        # ADD THE FULL STATIC PATH TO THE url = .... BELOW:
        ws.write_url(   row, 14, url = 'gendep/boxplots/'+d.boxplot_filename, string=d.boxplot_filename, tip='Boxplot image')

        # ws.insert_image(row, col, STATIC.....+d.boxplot_filename [, options]) # Optionally add the box-plots to excel file.
        # FileResponse objects¶


    # For large file could use:
    # FileResponse is a subclass of StreamingHttpResponse optimized for binary files. It uses wsgi.file_wrapper if provided by the wsgi server, otherwise it streams the file out in small chunks. FileResponse expects a file open in binary mode like so:
    # from django.http import FileResponse
    # response = FileResponse(open('myfile.png', 'rb'))


        
    response.write(xlsx_data)    # maybe add: mimetype='application/ms-excel'
    return response

"""
    
"""
  # Creates then downloads the currect dependency result table as an Excel file
  from openpyxl import Workbook
  from openpyxl.compat import range
  from openpyxl.cell import get_column_letter
  wb = Workbook()
  driver =
  tissue = All_tissues
  study = 'pmid'+... or All_studies
  dest_filename = 'dependency_%s_%s_%s.xlsx' %(driver,tissue,study)
  ws1 = wb.active
  ws1.title = "range names"
  for row in range(1, 40):
...     ws1.append(range(600))
  #ws2 = wb.create_sheet(title="Pi")
  # ws2['F5'] = 3.14

  for row in range(10, 20):
    for col in range(27, 54):
      _ = ws1.cell(column=col, row=row, value="%s" % get_column_letter(col))
>>> print(ws3['AA10'].value)
  # This will overwrite any existing file with the same name - so if another user tries to download this file at the same time, so maybe best to add a time stamp to file, then delay a second if file already exist, or add a suffix
  wb.save(filename = dest_filename)
"""

#def graph(request, driver_name):
#    return HttpResponse("You're looking at the graph for driver %s." % driver_name)

#def results(request, question_id):
#    response = "You're looking at the results of question %s."
#    return HttpResponse(response % question_id)

#def vote(request, question_id):
#    return HttpResponse("You're voting on question %s." % question_id)

