#!/usr/bin/env python

# The Windows 'py' launcher should also recognise the above shebang line.

# Script to import the data into the database tables
# An alternative if loading data into empty database is using 'Fixtures': https://docs.djangoproject.com/en/1.9/howto/initial-data/
# or django-adapters: http://stackoverflow.com/questions/14504585/good-ways-to-import-data-into-django
#                     http://django-adaptors.readthedocs.org/en/latest/

import os, csv
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # Full path to my django project directory, which is: "C:/Users/HP/Django_projects/cgdd/"  or: "/home/sbridgett/cgdd/"
# sys.path.append(PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")

# Needs the following django.setup(), otherwise get exception about: django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
# From google search, this django.setup() is called in the 'execute_from_command_line(sys.argv)' in the manage.py script
#    http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
#    http://grokbase.com/t/gg/django-users/14acvay7ny/upgrade-to-django-1-7-appregistrynotready-exception
import django
django.setup()


from gendep.models import Study, Gene, Drug, Dependency  # Removed: Histotype, 

def add_study(pmid, title, authors, description, summary, journal, pub_date):
  s, created = Study.objects.get_or_create( pmid=pmid, defaults={'title': title, 'authors': authors, 'description': description, 'summary': summary, 'journal': journal, 'pub_date': pub_date} )
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
  global ifull_name, isynonyms, iprev_names, ientrez_id, iensembl_id, icosmic_id, iomim_id, iuniprot_id, ivega_id, ihgnc_id
  print("\nLoading HGNC data")
  # Alternatively use the webservice: http://www.genenames.org/help/rest-web-service-help
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  for row in dataReader:
    if dataReader.line_num == 1: # The header line.
      ihgnc = dict() # The column name to number for the above HGNC dict. 
      for i in range(len(row)): ihgnc[row[i]] = i       # Store column numbers for each header item
      ifull_name  = ihgnc.get('name')            # eg: erb-b2 receptor tyrosine kinase 2
      isynonyms   = ihgnc.get('alias_symbol')    # eg: NEU|HER-2|CD340|HER2
      iprev_names = ihgnc.get('prev_symbol')     # eg: NGL
      ientrez_id  = ihgnc.get('entrez_id')       # eg: 2064
      iensembl_id = ihgnc.get('ensembl_gene_id') # eg: ENSG00000141736
      icosmic_id  = ihgnc.get('cosmic')          # eg: ERBB2
      iomim_id    = ihgnc.get('omim_id')         # eg: 164870
      iuniprot_id = ihgnc.get('uniprot_ids')     # eg: P04626  NOTE: This could be more than one Id
      ivega_id    = ihgnc.get('vega_id')         # eg: 
      ihgnc_id    = ihgnc.get('hgnc_id')         # eg: 
    else:
      gene_name = row[ihgnc['symbol']]    # The "ihgnc['symbol']" will be 1 - ie the second column, as 0 is first column which is HGNC number
      hgnc[gene_name] = row # Store the whole row for simplicity. 
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])
      


def find_or_add_gene(names, is_driver):  # names is a tuple of: gene_name, entrez_id, ensembl_id
  if   names[0]=='C8orf44.SGK3': names[0]='C8orf44-SGK3'  # as is hghc: 48354
  elif names[0]=='CTB.89H12.4':  names[0]='CTB-89H12.4'
  elif names[0]=='RP11.78H18.2': names[0]='RP11-78H18.2'
  elif names[0]=='C9orf96':      names[0]='STKLD1' # as C9orf96 is the old name.

  name = names[0]

  try:
    g = Gene.objects.get(gene_name=name)
    # Test if ensemble_id is same:
    if names[1] != '' and g.entrez_id != names[1]:
      if g.entrez_id != '':
        print("WARNING: For gene '%s': Entrez_id '%s' already saved in the Gene table doesn't match '%s' from the Excel file" %(g.gene_name,g.entrez_id,names[1]))
      else:
        print("Updating entrez_id, as driver must have been inserted as a target first:",g.gene_name,g.entrez_id,names[1])
        g.entrez_id=names[1]
        g.is_driver=is_driver
        g.save()
    if g.ensembl_id != names[2]: print("WARNING: For gene '%s': Ensembl_id '%s' already saved in the Gene table doesn't match '%s' from Excel file" %(g.gene_name, g.ensembl_id, names[2]) )

  except ObjectDoesNotExist: # Not found by the objects.get()
    if name not in hgnc:
      print("WARNING: Gene '%s' NOT found in HGNC dictionary" %(name) )
      g = Gene.objects.create(gene_name=name, is_driver=is_driver, entrez_id=names[1], ensembl_id=names[2])
    else:  
      this_hgnc = hgnc[name] # cache in a local variable to simplify code and reduce lookups.
      if names[1] != '' and names[1] != this_hgnc[ientrez_id]:
        print("WARNING: For gene '%s': entrez_id '%s' from HGNC doesn't match '%s' from Excel file" %(name, hgnc[name][ihgnc['entrez_id']], names[1]) )
        this_hgnc[ientrez_id] = names[1]        # So change it to use the one from the Excel file.
      if names[2] != this_hgnc[iensembl_id]:
        print("WARNING: For gene '%s': ensembl_id '%s' from HGNC doesn't match '%s' from Excel file" %(name, this_hgnc[iensembl_id], names[2]) )
        this_hgnc[iensembl_id] = names[2]  # So change it to use the one from the Excel file.
      # The following uses the file downloaded from HGNC, but alternatively can use a web service such as: mygene.info/v2/query?q=ERBB2&fields=HPRD&species=human     or: http://mygene.info/new-release-mygene-info-python-client-updated-to-v2-3-0/ or python client:  https://pypi.python.org/pypi/mygene   or uniprot: http://www.uniprot.org/help/programmatic_access  or Ensembl: http://rest.ensembl.org/documentation/info/xref_external
      g = Gene.objects.create(gene_name  = name,         # hgnc[name][ihgnc['symbol']]  eg. ERBB2
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
    
  return g



def import_data_from_tsv_table(csv_filepathname, table_name, study):
  print("\nImporting table: ",csv_filepathname)
  dataReader = csv.reader(open(csv_filepathname), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  
  counter = 0
  dependencies = []
  for row in dataReader:
    if dataReader.line_num == 1:
      if row[0] != 'Driver': print("***ERROR: Expected header to start with 'Driver', but found:",row)
      continue  # Ignore the header row, import everything else

    driver_gene = find_or_add_gene(split_driver_gene_name(row[0]), is_driver=True)
    target_gene = find_or_add_gene(split_target_gene_name(row[1]), is_driver=False)
    # If using Histotype table: histotype = find_or_add_histotype(row[3], full_name=None)  # was: if row[3] not in histotypes: histotypes.append(row[3])
    histotype = row[3] # As using CharField(choices=...) and now is validated in the model.
    mutation_type='Both'  # Default to 'Both' for current data now.

    # When loading the second table 'S1K', it contains duplicates of the Driver-Target pairs that were in 'S1I', which is ok as different histotype.
    # d = Dependency.objects.create(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], histotype=histotype, mutation_type=mutation_type, study=study)  # study=''
    # Using bulk_create() would be faster I think. See: http://vincent.is/speeding-up-django-postgres/  and https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
    
    # Bulk create is actually slightly slower than adding record by record
    d = Dependency(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], histotype=histotype, mutation_type=mutation_type, study=study)
    # if not d.is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
    dependencies.append( d )
    
    print("\r",counter, end=" ")
    counter += 1
    
  print("Bulk_create ....")  
  Dependency.objects.bulk_create(dependencies) # Comparisons for Postgres:  http://stefano.dissegna.me/django-pg-bulk-insert.html
  print("Finished importing table.")



if __name__ == "__main__":

  load_hgnc_dictionary()
  
  study_pmid = "Pending_0001"
  study_title = "Large Scale Profiling of Kinase Dependencies in Cancer Cell Line"
  study_authors = "James Campbell, Colm J. Ryan, Rachel Brough, Ilirjana Bajrami, Helen Pemberton, Irene Chong, Sara Costa-Cabral,Jessica Frankum, Aditi Gulati, Harriet Holme, Rowan Miller, Sophie Postel-Vinay, Rumana Rafiq, Wenbin Wei,Chris T Williamson, David A Quigley, Joe Tym, Bissan Al-Lazikani, Timothy Fenton, Rachael Natrajan, Sandra Strauss, Alan Ashworth and Christopher J Lord"
  study_description = "Summary: One approach to identifying cancer-specific vulnerabilities and novel therapeutic targets is to profile genetic dependencies in cancer cell lines. Here we use siRNA screening to estimate the genetic dependencies on 714 kinase and kinase-related genes in 117 different tumor cell lines. We provide this dataset as a resource and show that by integrating siRNA data with molecular profiling data, such as exome sequencing, candidate genetic dependencies associated with the mutation of specific cancer driver genescan be identified. By integrating the identified dependencies with interaction datasets, we demonstrate that the kinase dependencies associated with many cancer driver genes form dense connections on functional interaction networks. Finally, we show how this resource may be used to make predictions about the drug sensitivity of genetically or histologically defined subsets of cell lines, including an increased sensitivity of osteosarcoma cell lines to FGFR inhibitors and SMAD4 mutant tumor cells to mitotic inhibitors."
  study_summary = "siRNA screen of 714 kinase and kinase-related genes in 117 different tumor cell lines"
  study_journal = "Cell reports"
  study_pub_date = "2016"
  
  
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()
    # Before using atomic(), I tried "transaction.set_autocommit(False)" but got error "Your database backend doesn't behave properly when autocommit is off."
    print("\nEmptying database tables")
    for table in (Dependency, Study, Gene, Drug): table.objects.all().delete()  # removed: Histotype,

    study=add_study( study_pmid, study_title, study_authors, study_description, study_summary, study_journal, study_pub_date)
  
    for table_name in ('S1I', 'S1K'):
      csv_filepathname=os.path.join(PROJECT_DIR, os.path.join('input_data', 'Table_'+table_name+'_min_cols.txt'))   # Full path and name to the csv file
      import_data_from_tsv_table(csv_filepathname,table_name,study)
  # transaction.commit() # just needed if used "transaction.set_autocommit(False)"
