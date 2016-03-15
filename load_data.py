#!/usr/bin/env python

# The Windows 'py' launcher should also recognise the above shebang line.

# Script to import the data into the database tables
# An alternative if loading data into empty database is using 'Fixtures': https://docs.djangoproject.com/en/1.9/howto/initial-data/
# or django-adapters: http://stackoverflow.com/questions/14504585/good-ways-to-import-data-into-django
#                     http://django-adaptors.readthedocs.org/en/latest/


import os, csv, re
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from distutils import file_util  # Single file operations, eg: copy_file()
from django.db.models import Count # For the distincy study and target counts for drivers.

# In mysqlite database, the max_length parameter for fields is ignored as "Note that numeric arguments in parentheses that following the type name (ex: "VARCHAR(255)") are ignored by SQLite - SQLite does not impose any length restrictions (other than the large global SQLITE_MAX_LENGTH limit) on the length of strings, ...." (unless use sqlites CHECK contraint option)

# BUT MySQL does enforce max_length, so will truncate dtrings that are too long, so need to check for data truncation
import warnings # To convert the MySQL data truncation (due to field max_length being too small) into raising an exception."

# To use the warning category  below, might need to use: import MySQLdb
# Also see: http://www.nomadjourney.com/2010/04/suppressing-mysqlmysqldb-warning-messages-from-python/
# warnings.filterwarnings('error', category=MySQLdb.Warning) # Raises exceptions on a MySQL warning. From: http://stackoverflow.com/questions/2102251/trapping-a-mysql-warning
 # or:  warnings.filterwarnings('ignore', 'Unknown table .*')
warnings.filterwarnings('error', 'Data truncated .*') # regular expression to catch: Warning: Data truncated for column 'gene_name' at row 1
 
 # options are: (action, message='', category=Warning, module='', lineno=0, append=False)
 # message is a string containing a regular expression that the warning message must match (the match is compiled to always be case-insensitive). eg. Turncated ....
 # Can also run script with the "-W error" (or ignore) flag as for python.
 


 
FETCH_BOXPLOTS = True

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # Full path to my django project directory, which is: "C:/Users/HP/Django_projects/cgdd/"  or: "/home/sbridgett/cgdd/"
# sys.path.append(PROJECT_DIR)

# Paths to extract the boxplots images produced by R:
analysis_dir = "198_boxplots_for_Colm/analyses/"
combined_boxplots_dir = os.path.join(analysis_dir, "combined_histotypes_medium")
separate_boxplots_dir = os.path.join(analysis_dir, "separate_histotypes_medium")


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")

# Needs the following django.setup(), otherwise get exception about: django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
# From google search, this django.setup() is called in the 'execute_from_command_line(sys.argv)' in the manage.py script
#    http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
#    http://grokbase.com/t/gg/django-users/14acvay7ny/upgrade-to-django-1-7-appregistrynotready-exception
import django
django.setup()


from gendep.models import Study, Gene, Drug, Dependency  # Removed: Histotype, 


def fetch_boxplot(from_dir, to_dir, old_driver_name, driver_name, old_target_name,target_name, old_histotype, histotype, old_pmid, pmid):
  from_filename = "%s/%s_%s_%s__PMID%s.png" %(from_dir, old_driver_name, old_target_name, old_histotype, old_pmid)
  to_filename   = "%s/%s_%s_%s__PMID%s.png" %(to_dir, driver_name, target_name, histotype, pmid)
  # currently the pmid is: nnnnnnnn
#  if histotype == "PANCAN": 
#    fromfilename = "combined_boxplots_dir/%s_%s_allhistotypes__PMID%s.png" %(driver, target, pmid)  # eg: ABCB1_ALPK3_allhistotypes__PMIDnnnnnnnn.nng   or: ERBB2_MAP2K3_allhistotypes__PMIDnnnnnnnn or: ERBB2_C8orf44.SGK3_allhistotypes__PMIDnnnnnnnn
#    tofilename = %s_%s_allhistotypes__PMID%s.png" %(driver, target, pmid)
#  else:
#    fromfilename = "separate_boxplots_dir/%s_%s_%s__PMID%s.png" %(driver, target, histotype, pmid)  # eg: AKT2_ACVR1_LUNG__PMIDnnnnnnnn.png  or: ERBB2_MAP3K2_BREAST__PMIDnnnnnnnn
    #  or: filename = driver + "_" + target + "_" + histotype + "_" + "_PMIDnnnnnnnn.png"
  print( from_filename, " ====> ", to_filename)
  file_util.copy_file(from_filename, to_filename, preserve_mode=1, preserve_times=1, update=1, dry_run=0) 


def add_study(pmid, short_name, title, authors, abstract, summary, experiment_type, journal, pub_date):
  s, created = Study.objects.get_or_create( pmid=pmid, defaults={'short_name': short_name, 'title': title, 'authors': authors, 'abstract': abstract, 'summary': summary, 'experiment_type': experiment_type, 'journal': journal, 'pub_date': pub_date} )
  return s


def find_or_add_histotype(histotype, full_name):
  # if full_name is None: full_name={'PANCAN':'Pan cancer'}.get(histotype, histotype.title()) # The other known types are: 'BREAST', 'OSTEOSARCOMA', 'OESOPHAGUS', 'LUNG', and 'OVARY'
  # h, created = Histotype.objects.get_or_create(histotype=histotype, defaults={'full_name': full_name} )

  # As using the "choices=" param. 
  # if not Dependency().is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))  
  # else: 
  h = histotype
  
  return h


def split_driver_gene_name(long_name):
  names = long_name.split('_')    # Driver format is: CCND1_595_ENSG00000110092
  if len(names)!=3: print('ERROR: Invalid number of parts in driver gene, (as expected 3 parts)',long_name)
  return names


def split_target_gene_name(long_name):
  names = long_name.split('_')    # Target format is: DCK_ENSG00000156136
  if len(names)!=2:
    if names[0] == 'CDK12' and len(names)==3: # as "CDK12_ENSG00000167258_CRK7" is an exception to target format (CRK7 is an alternative name)
      names.pop()   # Remove the last 'CRK7' name from the names list
    else:
      print('Invalid number of parts in target gene, (as expected 2 parts)',long_name)
  names.insert(1,'') # or None, but Django stores None as empty string, rather than as null
  return names



hgnc = dict() # To read the HGNC ids into a dictionary
#ihgnc = dict() # The column name to number for the above HGNC dict. 
def load_hgnc_dictionary():
  global hgnc, isymbol, ifull_name, istatus, isynonyms, iprev_names, ientrez_id, iensembl_id, icosmic_id, iomim_id, iuniprot_id, ivega_id, ihgnc_id
  print("\nLoading HGNC data")
  # Alternatively use the webservice: http://www.genenames.org/help/rest-web-service-help
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      ihgnc = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): ihgnc[row[i]] = i       # Store column numbers for each header item
      isymbol     = ihgnc.get('symbol')
      ifull_name  = ihgnc.get('name')            # eg: erb-b2 receptor tyrosine kinase 2
      istatus     = ihgnc.get('status')
      isynonyms   = ihgnc.get('alias_symbol')    # eg: NEU|HER-2|CD340|HER2
      iprev_names = ihgnc.get('prev_symbol')     # eg: NGL
      ientrez_id  = ihgnc.get('entrez_id')       # eg: 2064
      iensembl_id = ihgnc.get('ensembl_gene_id') # eg: ENSG00000141736
      icosmic_id  = ihgnc.get('cosmic')          # eg: ERBB2
      iomim_id    = ihgnc.get('omim_id')         # eg: 164870
      iuniprot_id = ihgnc.get('uniprot_ids')     # eg: P04626  NOTE: This could be more than one Id
      ivega_id    = ihgnc.get('vega_id')         # eg: 
      ihgnc_id    = ihgnc.get('hgnc_id')         # eg: 
    elif row[istatus] == 'Entry Withdrawn':
       continue  # So skip this entry.
    else:
      gene_name = row[isymbol] # The "ihgnc['symbol']" will be 1 - ie the second column, as 0 is first column which is HGNC number
      cosmic_name = row[icosmic_id]
      if cosmic_name !='' and cosmic_name != gene_name:
        print("**** ERROR: COSMIC '%s' != gene_name '%s'" %(cosmic_name,gene_name))
      if gene_name in hgnc:
        print("*** ERROR: Duplicated gene_name '%s' status='%s' in HGNC file: Entrez: '%s' '%s' Ensembl '%s' '%s'" %(gene_name, row[istatus], hgnc[gene_name][ientrez_id], row[ientrez_id], hgnc[gene_name][iensembl_id], row[iensembl_id]), "\n",hgnc[gene_name], "\n",row )
      hgnc[gene_name] = row # Store the whole row for simplicity.
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])
      
def fix_gene_name(name):
  if   name == 'C8orf44.SGK3': return 'C8orf44-SGK3'  # as is hghc: 48354
  elif name == 'CTB.89H12.4':  return 'CTB-89H12.4'
  elif name == 'RP11.78H18.2': return 'RP11-78H18.2'
  elif name == 'C9orf96':      return 'STKLD1' # as C9orf96 is the old name.
  else: return name



RE_GENE_NAME = re.compile(r'^[0-9A-Za-z\-_\.]+$')

def find_or_add_gene(names, is_driver):  # names is a tuple of: gene_name, entrez_id, ensembl_id
  # if names[0] == 'PIK3CA' and is_driver: print("**** PIK3CA  is_driver: ",names)
  #global RE_GENE_NAME
  original_gene_name = names[0]
  names[0] = fix_gene_name(names[0])
  gene_name = names[0]
  entrez_id = names[1]
  ensembl_id = names[2]
  
  # Check that gene name_matches the current regexp in the gendep/urls.py file:
  assert RE_GENE_NAME.match(gene_name), "gene_name %s doesn't match regexp"%(gene_name)
  
  # if gene_name == 'PIK3CA': print("PIK3CA Here 0")
  try:
    # if gene_name == 'PIK3CA': print("PIK3CA Here A")
    g = Gene.objects.get(gene_name=gene_name)
    # Test driver status:
    if is_driver and not g.is_driver:
      print("Updating '%s' to is_driver" %(gene_name))
      g.is_driver = is_driver
      g.save()
    # Test if ensemble_id is same:
    if entrez_id != '' and g.entrez_id != entrez_id:
      if g.entrez_id != '':
        print("WARNING: For gene '%s': Entrez_id '%s' already saved in the Gene table doesn't match '%s' from the Excel file" %(g.gene_name,g.entrez_id,entrez_id))
      else:
        print("Updating entrez_id, as driver '%s' must have been inserted as a target first %s %s, is_driver=%s g.is_driver=%s" %(g.gene_name,g.entrez_id,entrez_id,is_driver,g.is_driver))
        g.entrez_id=entrez_id
        g.save()
    if g.ensembl_id != ensembl_id: print("WARNING: For gene '%s': Ensembl_id '%s' already saved in the Gene table doesn't match '%s' from Excel file" %(g.gene_name, g.ensembl_id, ensembl_id) )

  except ObjectDoesNotExist: # Not found by the objects.get()
    # if gene_name == 'PIK3CA': print("PIK3CA Here B")
    if gene_name not in hgnc:
      print("WARNING: Gene '%s' NOT found in HGNC dictionary" %(gene_name) )
      g = Gene.objects.create(gene_name=gene_name, original_name = original_gene_name, is_driver=is_driver, entrez_id=entrez_id, ensembl_id=ensembl_id)
    else:
      this_hgnc = hgnc[gene_name] # cache in a local variable to simplify code and reduce lookups.
      if entrez_id != '' and entrez_id != this_hgnc[ientrez_id]:
        print("WARNING: For gene '%s': entrez_id '%s' from HGNC doesn't match '%s' from Excel file" %(gene_name, this_hgnc[ientrez_id], entrez_id) )
        this_hgnc[ientrez_id] = entrez_id        # So change it to use the one from the Excel file.
      if ensembl_id != this_hgnc[iensembl_id]:
        print("WARNING: For gene '%s': ensembl_id '%s' from HGNC doesn't match '%s' from Excel file" %(gene_name, this_hgnc[iensembl_id], ensembl_id) )
        this_hgnc[iensembl_id] = ensembl_id  # So change it to use the one from the Excel file.
      # The following uses the file downloaded from HGNC, but alternatively can use a web service such as: mygene.info/v2/query?q=ERBB2&fields=HPRD&species=human     or: http://mygene.info/new-release-mygene-info-python-client-updated-to-v2-3-0/ or python client:  https://pypi.python.org/pypi/mygene   or uniprot: http://www.uniprot.org/help/programmatic_access  or Ensembl: http://rest.ensembl.org/documentation/info/xref_external
      g = Gene.objects.create(gene_name = gene_name,         # hgnc[gene_name][ihgnc['symbol']]  eg. ERBB2
               original_name = original_gene_name,
               is_driver  = is_driver,
               full_name  = this_hgnc[ifull_name],       # eg: erb-b2 receptor tyrosine kinase 2
               synonyms   = this_hgnc[isynonyms],        # eg: NEU|HER-2|CD340|HER2
               prev_names = this_hgnc[iprev_names],      # eg: NGL  # was: hgnc[name][iprevsymbol],
               entrez_id  = this_hgnc[ientrez_id],       # eg: 2064
               ensembl_id = this_hgnc[iensembl_id],      # eg: ENSG00000141736
               cosmic_id  = this_hgnc[icosmic_id],       # eg: ERBB2
               omim_id    = this_hgnc[iomim_id],         # eg: 164870
               uniprot_id = this_hgnc[iuniprot_id],      # eg: P04626
               vega_id    = this_hgnc[ivega_id],         # eg: OTTHUMG00000179300
               hgnc_id    = this_hgnc[ihgnc_id]
               # cancerrxgene_id = ....... ????
               # 'hgnc_id'          # eg: 3430
               # 'alias_name'       # eg: neuro/glioblastoma derived oncogene homolog|human epidermal growth factor receptor 2
               # 'gene_family'      # eg: CD molecules|Minor histocompatibility antigens|Erb-b2 receptor tyrosine kinases
               # 'refseq_accession' # eg: NM_004448
               )
    # print( "*****", this_hgnc[iuniprot_id])
    # g.save() # Using create() above instead of Gene(...) and g.save.
    
  # if gene_name == 'PIK3CA': print("PIK3CA Here C")
  return g

def get_boxplot_histotype(histotype):
    # As the R scripts used some different tissue names
    if   histotype == "PANCAN": return "allhistotypes"
    elif histotype == "OSTEOSARCOMA": return "BONE"
    # elif histotype == "BREAST": return "BREAST",
    # elif histotype == "LUNG": return "LUNG",
    # elif histotype == "": return "HEADNECK",
    # elif histotype == "": return "PANCREAS",
    # elif histotype == "": return "CERVICAL",
    # elif histotype == "OVARY": return "OVARY",
    # elif histotype == "OESOPHAGUS": return "OESOPHAGUS",
    # elif histotype == "": return "ENDOMETRIUM",
    # elif histotype == "": return "CENTRAL_NERVOUS_SYSTEM"
    else: return histotype

# driver_counter = dict() # To count the number of times each driver is added to the database
def import_data_from_tsv_table(csv_filepathname, table_name, study, study_old_pmid):
  global FETCH_BOXPLOTS
  print("\nImporting table: ",csv_filepathname)
  print("FETCH_BOXPLOTS is: ",FETCH_BOXPLOTS)

  dataReader = csv.reader(open(csv_filepathname), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  
  count_added = 0
  count_skipped = 0
  dependencies = []
  for row in dataReader:
    if dataReader.line_num == 1:
      if row[0] != 'Driver': print("***ERROR: Expected header to start with 'Driver', but found:",row)
      continue  # Ignore the header row, import everything else

    if float(row[2]) > 0.05:
      count_skipped += 1
      continue  # Skip as the wilcox_p value isn't significant

    driver_gene = find_or_add_gene(split_driver_gene_name(row[0]), is_driver=True)
    target_gene = find_or_add_gene(split_target_gene_name(row[1]), is_driver=False)
    # If using Histotype table: histotype = find_or_add_histotype(row[3], full_name=None)  # was: if row[3] not in histotypes: histotypes.append(row[3])
    histotype = row[3] # As using CharField(choices=...) and now is validated in the model.
    mutation_type='Both'  # Default to 'Both' for current data now.

    # When loading the second table 'S1K', it contains duplicates of the Driver-Target pairs that were in 'S1I', which is ok as different histotype.
    # d = Dependency.objects.create(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], histotype=histotype, mutation_type=mutation_type, study=study)  # study=''
    # Using bulk_create() would be faster I think. See: http://vincent.is/speeding-up-django-postgres/  and https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
    
    # Bulk create is actually slightly slower than adding record by record
    d = Dependency(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], effect_size="", histotype=histotype, mutation_type=mutation_type, study=study)
    # As inhibitors is a ManyToMany field so can't just assign it with: inhibitors=None, 
    # if not d.is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
    dependencies.append( d )


    # Fetch the boxplot:
    if FETCH_BOXPLOTS:
      from_dir = combined_boxplots_dir if row[3] == "PANCAN" else separate_boxplots_dir
      to_dir = "gendep/static/gendep/boxplots"
      old_histotype = get_boxplot_histotype(histotype)
      fetch_boxplot(from_dir, to_dir, driver_gene.original_name, driver_gene.gene_name, target_gene.original_name, target_gene.gene_name, old_histotype, histotype,  study_old_pmid, study.pmid)

    print("\r",count_added, end=" ")
    count_added += 1
  
  print( "%d dependency rows were skipped as wilcox_p > 0.05" %(count_skipped))
  print("Bulk_create ....")  
  Dependency.objects.bulk_create(dependencies) # Comparisons for Postgres:  http://stefano.dissegna.me/django-pg-bulk-insert.html
  print("Finished importing table.")


def add_counts_of_study_tissue_and_target_to_drivers():
  print("Adding study, tissue and target counts to drivers")
  # select driver, count(distinct target), count(distinct pmid) from gendep_dependency group by driver;
  counts = Dependency.objects.values('driver').annotate( num_studies=Count('study', distinct=True), num_histotypes=Count('histotype', distinct=True), num_targets=Count('target', distinct=True) )
  # There is probably a faster SQL type quesry, or bulk_update
  for row in counts:
    try:
      print("gene_name: %s %d %d %d" %(row['driver'], row['num_studies'], row['num_histotypes'], row['num_targets']))
      g = Gene.objects.get(gene_name=row['driver'])  # .gene_name
      
      # Double-check that name is same:
      if g.gene_name != row['driver']:
        print("*** ERROR: count gene_name mismatch for '%s' and '%s'" %(g.gene_name,row['driver']))
      elif not g.is_driver: 
        print("*** ERROR: count gene isn't marked as a driver '%s'" %(g.gene_name))
      else:
        g.num_studies = row['num_studies']
        g.num_histotypes = row['num_histotypes']
        g.num_targets = row['num_targets']
        g.save()
    except ObjectDoesNotExist: # Not found by the objects.get()
      print("*** ERROR: driver gene_name % NOT found in the Gene table: '%s'" %(row['driver']))
  print("Finished adding study and target counts to drivers")

    
    
if __name__ == "__main__":

  load_hgnc_dictionary()
  
  study_pmid = "26947069"
  study_short_name = "Campbell(2016)"
  study_title = "Large Scale Profiling of Kinase Dependencies in Cancer Cell Line"
  study_authors = "James Campbell, Colm J. Ryan, Rachel Brough, Ilirjana Bajrami, Helen Pemberton, Irene Chong, Sara Costa-Cabral,Jessica Frankum, Aditi Gulati, Harriet Holme, Rowan Miller, Sophie Postel-Vinay, Rumana Rafiq, Wenbin Wei,Chris T Williamson, David A Quigley, Joe Tym, Bissan Al-Lazikani, Timothy Fenton, Rachael Natrajan, Sandra Strauss, Alan Ashworth and Christopher J Lord"
  study_abstract = "One approach to identifying cancer-specific vulnerabilities and novel therapeutic targets is to profile genetic dependencies in cancer cell lines. Here we use siRNA screening to estimate the genetic dependencies on 714 kinase and kinase-related genes in 117 different tumor cell lines. We provide this dataset as a resource and show that by integrating siRNA data with molecular profiling data, such as exome sequencing, candidate genetic dependencies associated with the mutation of specific cancer driver genescan be identified. By integrating the identified dependencies with interaction datasets, we demonstrate that the kinase dependencies associated with many cancer driver genes form dense connections on functional interaction networks. Finally, we show how this resource may be used to make predictions about the drug sensitivity of genetically or histologically defined subsets of cell lines, including an increased sensitivity of osteosarcoma cell lines to FGFR inhibitors and SMAD4 mutant tumor cells to mitotic inhibitors."
  study_summary = "siRNA screen of 714 kinase and kinase-related genes in 117 different tumor cell lines"
  experiment_type = "kinome siRNA"
  study_journal = "Cell reports"
  study_pub_date = "2016, 2 Mar"
  study_old_pmid = "nnnnnnnn" # This is the ID assigned to boxplots by the R script at present, but can change this in future to be same as the actual pmid.
  study_old_pmid = "26947069"
 
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()
    # Before using atomic(), I tried "transaction.set_autocommit(False)" but got error "Your database backend doesn't behave properly when autocommit is off."
    print("\nEmptying database tables")
    for table in (Dependency, Study, Gene, Drug): table.objects.all().delete()  # removed: Histotype,

    study=add_study( study_pmid, study_short_name, study_title, study_authors, study_abstract, study_summary, experiment_type, study_journal, study_pub_date)
  
    for table_name in ('S1I', 'S1K'):
      csv_filepathname=os.path.join(PROJECT_DIR, os.path.join('input_data', 'Table_'+table_name+'_min_cols.txt'))   # Full path and name to the csv file
      import_data_from_tsv_table(csv_filepathname, table_name, study, study_old_pmid)
  # transaction.commit() # just needed if used "transaction.set_autocommit(False)"

  
    # Project Achilles: # https://www.broadinstitute.org/achilles  and http://www.nature.com/articles/sdata201435
    study_pmid = "25984343"
    study_short_name = "Cowley(2014)"
    study_title = "Parallel genome-scale loss of function screens in 216 cancer cell lines for the identification of context-specific genetic dependencies."
    study_authors = "Cowley GS, Weir BA, Vazquez F, Tamayo P, Scott JA, Rusin S, East-Seletsky A, Ali LD, Gerath WF, Pantel SE, Lizotte PH, Jiang G, Hsiao J, Tsherniak A, Dwinell E, Aoyama S, Okamoto M, Harrington W, Gelfand E, Green TM, Tomko MJ, Gopal S, Wong TC, Li H, Howell S, Stransky N, Liefeld T, Jang D, Bistline J, Hill Meyers B, Armstrong SA, Anderson KC, Stegmaier K, Reich M, Pellman D, Boehm JS, Mesirov JP, Golub TR, Root DE, Hahn WC"
    study_abstract = "Using a genome-scale, lentivirally delivered shRNA library, we performed massively parallel pooled shRNA screens in 216 cancer cell lines to identify genes that are required for cell proliferation and/or viability. Cell line dependencies on 11,000 genes were interrogated by 5 shRNAs per gene. The proliferation effect of each shRNA in each cell line was assessed by transducing a population of 11M cells with one shRNA-virus per cell and determining the relative enrichment or depletion of each of the 54,000 shRNAs after 16 population doublings using Next Generation Sequencing. All the cell lines were screened using standardized conditions to best assess differential genetic dependencies across cell lines. When combined with genomic characterization of these cell lines, this dataset facilitates the linkage of genetic dependencies with specific cellular contexts (e.g., gene mutations or cell lineage). To enable such comparisons, we developed and provided a bioinformatics tool to identify linear and nonlinear correlations between these features."
    study_summary = "shRNA screen of 11,000 genes in 216 different cancer cell lines, with 5 shRNAs per gene"
    experiment_type = "genome shRNA"
    study_journal = "Scientific Data"
    study_pub_date = "2014, 30 Sep"
    study_old_pmid = "25984343"
    study=add_study( study_pmid, study_short_name, study_title, study_authors, study_abstract, study_summary, experiment_type, study_journal, study_pub_date )
  
  
    add_counts_of_study_tissue_and_target_to_drivers()