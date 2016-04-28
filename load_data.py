#!/usr/bin/env python

# The Windows 'py' launcher should also recognise the above shebang line.

# Add the Effect size results now - present as percentage values - so x100
# No longer using the target variants - only keep the variant with the lowest (ie. best) p-value.
# Do the annotation with entrez, ensembl, etc as a separate script later.
# Add the ensembl_protein - as is used by StringDB for interactions.


# Script to import the data into the database tables
# An alternative if loading data into empty database is using 'Fixtures': https://docs.djangoproject.com/en/1.9/howto/initial-data/
# or django-adapters: http://stackoverflow.com/questions/14504585/good-ways-to-import-data-into-django
#                     http://django-adaptors.readthedocs.org/en/latest/

import sys, os, csv, re
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from distutils import file_util  # Single file operations, eg: copy_file()
from django.db.models import Count # For the distinct study and target counts for drivers.

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
 


 
FETCH_BOXPLOTS = False # True # False # True # Should also test that is running on development computer.
ACHILLES_FETCH_BOXPLOTS = False # True # False # True # Should also test that is running on development computer.
COLT_FETCH_BOXPLOTS = True # False

# Build paths inside the project like this: os.path.join(PROJECT_DIR, ...)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__)) # Full path to my django project directory, which is: "C:/Users/HP/Django_projects/cgdd/"  or: "/home/sbridgett/cgdd/"
# sys.path.append(PROJECT_DIR)

# Paths to extract the boxplots images produced by R:
analysis_dir = "198_boxplots_for_Colm/analyses/"
combined_boxplots_dir = os.path.join(analysis_dir, "combined_histotypes_medium")
separate_boxplots_dir = os.path.join(analysis_dir, "separate_histotypes_medium")

#/c/Users/HP/Django_projects/cgdd/198_boxplots_for_Colm/analyses
#Achilles_analysis_dir = ..... ""
Achilles_combined_boxplots_dir = os.path.join(analysis_dir, "combined_histotypes_achilles")
Achilles_separate_boxplots_dir = os.path.join(analysis_dir, "separate_histotypes_achilles")

# As colt is only breast data then no combined data boxplots:
Colt_separate_boxplots_dir = os.path.join(analysis_dir, "separate_histotypes_colt_allbreast")

static_gendep_boxplot_dir = "gendep/static/gendep/boxplots"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")

# Needs the following django.setup(), otherwise get exception about: django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
# From google search, this django.setup() is called in the 'execute_from_command_line(sys.argv)' in the manage.py script
#    http://stackoverflow.com/questions/25537905/django-1-7-throws-django-core-exceptions-appregistrynotready-models-arent-load
#    http://grokbase.com/t/gg/django-users/14acvay7ny/upgrade-to-django-1-7-appregistrynotready-exception
import django
django.setup()


from gendep.models import Study, Gene, Drug, Dependency  # Removed: Histotype, 

def make_AtoZ_subdirs(to_dir):  
  for i in range(ord('A'), ord('Z')+1):
    to_dir_subdir = to_dir + '/' + chr(i)
    if not os.path.exists(to_dir_subdir): os.mkdir(to_dir_subdir)


def fetch_boxplot(from_dir, to_dir, old_driver_name, driver_name, old_target_name,target_name, old_histotype, histotype, old_pmid, pmid):
  from_filename = "%s/%s_%s_%s__PMID%s.png" %(from_dir, old_driver_name, old_target_name, old_histotype, old_pmid)
  if not os.path.exists(from_filename): # As mostly already changed in Achilles data
      from_filename = "%s/%s_%s_%s__PMID%s.png" %(from_dir, old_driver_name, target_name, old_histotype, old_pmid)
  
  to_dir_subdir = to_dir+'/' + driver_name[:1] # Storing in A-Z subdirectories to let OS find file a bit faster.
  # if not os.path.exists(to_dir_subdir): os.mkdir(to_dir_subdir) Already created by make_AtoZ_subdirs()
  
  to_filename   = "%s/%s_%s_%s__PMID%s.png" %(to_dir_subdir, driver_name, target_name, histotype, pmid)
  
  # currently the pmid is: nnnnnnnn
#  if histotype == "PANCAN": 
#    fromfilename = "combined_boxplots_dir/%s_%s_allhistotypes__PMID%s.png" %(driver, target, pmid)  # eg: ABCB1_ALPK3_allhistotypes__PMIDnnnnnnnn.nng   or: ERBB2_MAP2K3_allhistotypes__PMIDnnnnnnnn or: ERBB2_C8orf44.SGK3_allhistotypes__PMIDnnnnnnnn
#    tofilename = %s_%s_allhistotypes__PMID%s.png" %(driver, target, pmid)
#  else:
#    fromfilename = "separate_boxplots_dir/%s_%s_%s__PMID%s.png" %(driver, target, histotype, pmid)  # eg: AKT2_ACVR1_LUNG__PMIDnnnnnnnn.png  or: ERBB2_MAP3K2_BREAST__PMIDnnnnnnnn
    #  or: filename = driver + "_" + target + "_" + histotype + "_" + "_PMIDnnnnnnnn.png"
  # print( from_filename, " ====> ", to_filename)
  file_util.copy_file(from_filename, to_filename, preserve_mode=1, preserve_times=1, update=1, dry_run=0) 


def add_study(pmid, code, short_name, title, authors, abstract, summary, experiment_type, journal, pub_date):
  s, created = Study.objects.get_or_create( pmid=pmid, defaults={'code': code, 'short_name': short_name, 'title': title, 'authors': authors, 'abstract': abstract, 'summary': summary, 'experiment_type': experiment_type, 'journal': journal, 'pub_date': pub_date} )
  return s


def find_or_add_histotype(histotype, full_name):
  # if full_name is None: full_name={'PANCAN':'Pan cancer'}.get(histotype, histotype.title()) # The other known types are: 'BREAST', 'OSTEOSARCOMA', 'OESOPHAGUS', 'LUNG', and 'OVARY'
  # h, created = Histotype.objects.get_or_create(histotype=histotype, defaults={'full_name': full_name} )

  # As using the "choices=" param. 
  # if not Dependency().is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))  
  # else: 
  h = histotype
  
  return h


driver_name_warning_already_reported = dict()
def split_driver_gene_name(long_name):
  names = long_name.split('_')    # Driver format is: CCND1_595_ENSG00000110092  
  if len(names)!=3 and long_name not in driver_name_warning_already_reported:
      print('ERROR: Invalid number of parts in driver gene, (as expected 3 parts)',long_name)
      driver_name_warning_already_reported[long_name] = None
  if not names[1].isdigit() and long_name not in driver_name_warning_already_reported:
      print("** ERROR: Expected integer for Entrez id second part of name '%s'"  %(long_name))
      driver_name_warning_already_reported[long_name] = None
  if names[2][:4] != 'ENSG' and names[2]!='NoEnsemblIdFound' and long_name not in driver_name_warning_already_reported:
      print("ERROR: Expected 'ENSG' for start of driver ensembl name: '%s'" %(long_name))
      driver_name_warning_already_reported[long_name] = None
  # eg: In the data from R, there are several drivers with two or more ensembl gane names:
  #
  #  EIF1AX_101060318_ENSG00000173674_ENSG00000198692
  #  HIST1H3B_3020_ENSG00000132475_ENSG00000163041
  #  TRIM48_101930235_ENSG00000150244_ENSG00000223417
  #  RGPD3_653489_ENSG00000015568_ENSG00000153165_ENSG00000183054
  #  MEF2BNB.MEF2B_729991_ENSG00000064489_ENSG00000254901
  #  HIST1H2BF_8347_ENSG00000168242_ENSG00000180596_ENSG00000187990_ENSG00000197697_ENSG00000197846
  #  NUTM2F_441457_ENSG00000130950_ENSG00000188152
  #  H3F3B_3021_ENSG00000132475_ENSG00000163041
  #  WDR33_84826_ENSG00000136709_ENSG00000173349
  #  KRTAP4.11_728224_ENSG00000204880_ENSG00000212721
  return names


target_name_warning_already_reported = dict()
def split_target_gene_name(long_name, isColt):

  names = long_name.split('_')    # Target format is: DCK_ENSG00000156136 for Campbell and Achilles, but for Colt is: ATP1A1_476
  if len(names)!=2:
    if names[0] == 'CDK12' and len(names)==3 and names[2]=='CRK7': # as "CDK12_ENSG00000167258_CRK7" is an exception to target format (CRK7 is an alternative name)
      names.pop()   # Remove the last 'CRK7' name from the names list
    elif long_name not in target_name_warning_already_reported:
      print('Invalid number of parts in target gene, (as expected 2 parts)',long_name)
      target_name_warning_already_reported[long_name] = None

  if isColt:
    names.append('') # As Colt names have entrez id, but not ensembl id.  
  else:
    if names[1][:4] != 'ENSG' and names[1]!='NoEnsemblIdFound' and long_name not in target_name_warning_already_reported:
      print("ERROR: Expected 'ENSG' for start of target ensembl name: '%s'" %(long_name))
      target_name_warning_already_reported[long_name] = None
      
    names.insert(1,'') # (or None, but Django stores None as empty string, rather than as null) to make same number of elements in names array for target names as in driver names.
    
  return names



hgnc = dict() # To read the HGNC ids into a dictionary
#ihgnc = dict() # The column name to number for the above HGNC dict. 
def load_hgnc_dictionary():
  global hgnc, isymbol, ifull_name, istatus, isynonyms, iprev_names, ientrez_id, iensembl_id, icosmic_id, iomim_id, iuniprot_id, ivega_id, ihgnc_id
  print("\nLoading HGNC data")
  # Alternatively use the webservice: http://www.genenames.org/help/rest-web-service-help
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  row = next(dataReader) # To read the first heading line. See: http://stackoverflow.com/questions/17262256/reading-one-line-of-csv-data-in-python
  # or Pandas might be faster? eg: import pandas as pd;   data = pd.read_csv("names.csv", nrows=1)
  # was if dataReader.line_num == 1: # The header line.
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
  
  # Then read the rest of the lines:
  for row in dataReader:      
    if row[istatus] == 'Entry Withdrawn':
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


ATARmap = dict()
def load_mygene_hgnc_dictionary():
  # Reads in the names for the genes used in the R analysis of Achilles data
  global ATARmap, jsol_entrez, img_entrezgene, img_symbol, img_hgnc, ihgnc_ensembl_id, img_ensembl_id, iname_used_for_R

  # The following file is produced by parse_Achilles_QC_v243_rna_Gs_gct.py:
  output_file4_newnames = os.path.join("Achilles_data", "Achilles_solname_to_entrez_map_with_names_used_for_R_v3_12Mar2016.txt")
  print("\nLoading ATARmap mygne dictionary from file:", output_file4_newnames)
  
  dataReader = csv.reader(open(output_file4_newnames), dialect='excel-tab')
  # Format for file:
  # sol.name        mg_symbol       entrez  mg_entrez  mg_hgnc  hgnc_ensembl     mg_ensembl       name_used_for_R
  # A2ML1_1_01110   A2ML1           144568  144568     23336    ENSG00000166535  ENSG00000166535  A2ML11_ENSG00000166535

  row = next(dataReader) # To read the first heading line.
  # if dataReader.line_num == 1: # The header line.
  cols = dict() # The column name to number for the above HGNC dict. 
  for i in range(len(row)): cols[row[i]] = i       # Store column numbers for each header item
  jsol_name  = cols['sol.name']  # eg: A2ML1_1_01110      
  jsol_entrez = cols['entrez']
  img_entrezgene = cols['mg_entrez']
  img_symbol = cols['mg_symbol']
  img_hgnc = cols['mg_hgnc']
  ihgnc_ensembl_id = cols['hgnc_ensembl']
  img_ensembl_id = cols['mg_ensembl']
  iname_used_for_R = cols['name_used_for_R']
  # for row in dataReader:      
    #else:
      # Need to fix this for row:
      # Loading ATARmap mygne dictionary from file: Achilles_data\Achilles_solname_to_entrez_map_with_names_used_for_R_v3_12Mar2016.txt
      # ERROR: iname_used_for_R=7 > len(row)=7 ['ZZEF1_1_1110', 'ZZEF1', '23140', '23140', '29027', 'ENSG00000074755', 'ENSG00000074755']
      #if iname_used_for_R >= len(row): print("ERROR: iname_used_for_R=%d > len(row)=%d" %(iname_used_for_R,len(row)), row)
      #key = row[iname_used_for_R]
      #if key in ATARmap:
      #  print("*** Warning: Duplicate name_used_for_R %s in file: " %(key),row)
      #ATARmap[key] = row


RE_GENE_NAME = re.compile(r'^[0-9A-Za-z\-_\.]+$')

def find_or_add_gene(names, is_driver, is_target, isAchilles, isColt):  # names is a tuple of: gene_name, entrez_id, ensembl_id
  # if names[0] == 'PIK3CA' and is_driver: print("**** PIK3CA  is_driver: ",names)
  #global RE_GENE_NAME
#  if isAchilles: names[0] = names[0][:-1]  # Remove the final character from end of the string - but this will mean extra records for some dependecies
  # The above trimming of the varaint number from Achilles is already done by the calling function.

  # Things to fix for Achilles data:
      # For gene 'DUX3': ensembl_id '' from HGNC doesn't match 'NoEnsemblIdFound' from Excel file
      # Invalid number of parts in target gene, (as expected 2 parts) GTF2H2C_21_ENSG00000274675
      #     - is in the "Achilles_solname_to_entrez_map_with_names_used_for_R_v3_12Mar2016.txt" as:
      #       GTF2H2D_1_10001 GTF2H2C_2       730394  730394  35418           ENSG00000274675
      # WARNING: For gene 'GTF2H2': Ensembl_id 'ENSG00000145736' already saved in the Gene table doesn't match '21' from Excel file
      # Invalid number of parts in target gene, (as expected 2 parts) C4B_21_ENSG00000233312
      
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
    if is_target and not g.is_target:
      print("Updating '%s' to is_target" %(gene_name))
      g.is_target = is_target
      g.save()
      
    # Test if ensemble_id is same:
    if entrez_id != '' and g.entrez_id != entrez_id:
      if g.entrez_id != '':
        print("WARNING: For gene '%s': Entrez_id '%s' already saved in the Gene table doesn't match '%s' from the Excel file" %(g.gene_name,g.entrez_id,entrez_id))
      else:
        print("Updating entrez_id, as driver '%s' must have been inserted as a target first %s %s, is_driver=%s g.is_driver=%s, g.is_target=%s" %(g.gene_name,g.entrez_id,entrez_id,is_driver,g.is_driver, g.is_target))
        g.entrez_id=entrez_id
        g.save()
    if g.ensembl_id != ensembl_id: print("WARNING: For gene '%s': Ensembl_id '%s' already saved in the Gene table doesn't match '%s' from Excel file" %(g.gene_name, g.ensembl_id, ensembl_id) )

  except ObjectDoesNotExist: # Not found by the objects.get()
    # if gene_name == 'PIK3CA': print("PIK3CA Here B")
    if gene_name not in hgnc:
      print("WARNING: Gene '%s' NOT found in HGNC dictionary" %(gene_name) )
      g = Gene.objects.create(gene_name=gene_name, original_name = original_gene_name, is_driver=is_driver, is_target=is_target, entrez_id=entrez_id, ensembl_id=ensembl_id)
    else:
      this_hgnc = hgnc[gene_name] # cache in a local variable to simplify code and reduce lookups.
      if entrez_id != '' and entrez_id != this_hgnc[ientrez_id]:
        print("WARNING: For gene '%s': entrez_id '%s' from HGNC doesn't match '%s' from Excel file" %(gene_name, this_hgnc[ientrez_id], entrez_id) )
        this_hgnc[ientrez_id] = entrez_id        # So change it to use the one from the Excel file.
      if entrez_id != '' and entrez_id != 'NoEnsemblIdFound' and ensembl_id != this_hgnc[iensembl_id]:
        print("WARNING: For gene '%s': ensembl_id '%s' from HGNC doesn't match '%s' from Excel file" %(gene_name, this_hgnc[iensembl_id], ensembl_id) )
        this_hgnc[iensembl_id] = ensembl_id  # So change it to use the one from the Excel file.
      # The following uses the file downloaded from HGNC, but alternatively can use a web service such as: mygene.info/v2/query?q=ERBB2&fields=HPRD&species=human     or: http://mygene.info/new-release-mygene-info-python-client-updated-to-v2-3-0/ or python client:  https://pypi.python.org/pypi/mygene   http://docs.mygene.info/en/latest/doc/query_service.html  Fields available:  http://mygene.info/v2/gene/1017     http://docs.mygene.info/en/latest/
      # or uniprot: http://www.uniprot.org/help/programmatic_access  or Ensembl: http://rest.ensembl.org/documentation/info/xref_external
#      if info_source == 'HGNC':
      prevname_synonyms = this_hgnc[iprev_names] + ('' if this_hgnc[iprev_names] == '' or this_hgnc[isynonyms] == '' else '|') + this_hgnc[isynonyms]
      
      # In HGNC some genes have two or three OMIM IDs, eg: gene "ATRX" has omim_id: "300032|300504" (length=13, but column width is 10, and simpler to just store first name)
      if len(this_hgnc[iomim_id]) >= 9:
          pos = this_hgnc[iomim_id].find('|')
          if pos > -1: this_hgnc[iomim_id] = this_hgnc[iomim_id][:pos]
          
      g = Gene.objects.create(gene_name = gene_name,         # hgnc[gene_name][ihgnc['symbol']]  eg. ERBB2
               original_name = original_gene_name,
               is_driver  = is_driver,
               is_target  = is_target,
               full_name  = this_hgnc[ifull_name],       # eg: erb-b2 receptor tyrosine kinase 2
               # synonyms   = this_hgnc[isynonyms],        # eg: NEU|HER-2|CD340|HER2
               # prev_names = this_hgnc[iprev_names],      # eg: NGL  # was: hgnc[name][iprevsymbol],
               prevname_synonyms = prevname_synonyms,
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
      """
      elif info_source == 'MYGENE_HGNC_FILE':
        key = gene_name+'_'+ensembl_id
        if key in ATARmap:
          
        img_hgnc
        gene_name = names[0]
  entrez_id = names[1]
  ensembl_id = names[2]
        ATARmap, jsol_entrez, img_entrezgene, img_symbol, img_hgnc, ihgnc_ensembl_id, img_ensembl_id, iname_used_for_R
        g = Gene.objects.create(gene_name = gene_name,         # hgnc[gene_name][ihgnc['symbol']]  eg. ERBB2
               original_name = original_gene_name,
               is_driver  = is_driver,
               is_target  = is_target,
               full_name  = this_hgnc[ifull_name],       # eg: erb-b2 receptor tyrosine kinase 2
               synonyms   = this_hgnc[isynonyms],        # eg: NEU|HER-2|CD340|HER2
               prev_names = this_hgnc[iprev_names],      # eg: NGL  # was: hgnc[name][iprevsymbol],
               entrez_id  = ATARmap[ientrez_id],       # eg: 2064
               ensembl_id = ATARmap[iensembl_id],      # eg: ENSG00000141736
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
      else: print("Invalid Iinfo_source='%s'" %(info_source))
      """
    # print( "*****", this_hgnc[iuniprot_id])
    # g.save() # Using create() above instead of Gene(...) and g.save.
    
  # if gene_name == 'PIK3CA': print("PIK3CA Here C")
  return g


  
def get_boxplot_histotype(histotype):
    # As the R scripts used some different tissue names
    # if   histotype == "PANCAN": return "allhistotypes"  # BUT the "run_Intercell_analysis.R" is changed now to use "PANCAN"
    if histotype == "OSTEOSARCOMA": return "BONE"
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


def fetch_boxplot_file(driver_gene, target_gene, histotype, isAchilles, isColt, target_variant=''):
    global static_gendep_boxplot_dir
    if isAchilles:
      from_dir = Achilles_combined_boxplots_dir if histotype == "PANCAN" else Achilles_separate_boxplots_dir 
      target_gene_name = target_gene.gene_name + target_variant
      target_gene_original_name = target_gene.original_name + target_variant # As already fixed before running R
        # This used old name: 'C8orf44.SGK3' # 'C8orf44-SGK3' is new name in hghc: 48354
        # This used new name: 'STKLD1' # C9orf96 is the old name.
    elif isColt:
      if histotype == "PANCAN": print("**** ERROR: Cannot have PANCAN for Colt data *****")
      from_dir = Colt_separate_boxplots_dir
      target_gene_name = target_gene.gene_name
      target_gene_original_name = target_gene.original_name      
    else:
      from_dir = combined_boxplots_dir if histotype == "PANCAN" else separate_boxplots_dir
      target_gene_name = target_gene.gene_name
      target_gene_original_name = target_gene.original_name
       
    to_dir = static_gendep_boxplot_dir
    old_histotype = get_boxplot_histotype(histotype)
    fetch_boxplot(from_dir, to_dir, driver_gene.original_name, driver_gene.gene_name, target_gene_original_name, target_gene_name, old_histotype, histotype,  study_old_pmid, study.pmid)
    
    
# driver_counter = dict() # To count the number of times each driver is added to the database
def import_data_from_tsv_table(csv_filepathname, table_name, study, study_old_pmid):
  global FETCH_BOXPLOTS
  print("\nImporting table: ",csv_filepathname)
  print("FETCH_BOXPLOTS is: ",FETCH_BOXPLOTS)

  effect_size = -1
  print("**** import_data_from_tsv_table: Setting effect size to %f" %(effect_size))
  
  # marker  target  nA      nB      wilcox.p        CLES  [tissue - only in bytissue files]
  # MYC_4609_ENSG00000136997        AAK1_ENSG00000115977    20      60      0.866757954072364       0.417083333333333   BREAST

  # whereas original format in "Table_S1I_min_cols.txt" was:
  # Driver  Target  wilcox.p        Histotype       PMID
  # CDKN2A_1029_ENSG00000147889     NEK9_ENSG00000119638    0.021600446     PANCAN

  dataReader = csv.reader(open(csv_filepathname), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  
  count_added = 0
  count_skipped = 0
  dependencies = []
  
  row = next(dataReader) # To read the first heading line.
  if row[0] != 'Driver': print("***ERROR: Expected header to start with 'Driver', but found:",row)
      
  for row in dataReader:
    if float(row[2]) > 0.05:
      count_skipped += 1
      continue  # Skip as the wilcox_p value isn't significant

    driver_gene = find_or_add_gene(split_driver_gene_name(row[0]), is_driver=True, is_target=False, isAchilles=False, isColt=False)
    target_gene = find_or_add_gene(split_target_gene_name(row[1]), is_driver=False, is_target=True, isAchilles=False, isColt=False)
    # If using Histotype table: histotype = find_or_add_histotype(row[3], full_name=None)  # was: if row[3] not in histotypes: histotypes.append(row[3])
    histotype = row[3] # As using CharField(choices=...) and now is validated in the model.
    mutation_type='Both'  # Default to 'Both' for current data now.

    # When loading the second table 'S1K', it contains duplicates of the Driver-Target pairs that were in 'S1I', which is ok as different histotype.
    # d = Dependency.objects.create(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], histotype=histotype, mutation_type=mutation_type, study=study)  # study=''
    # Using bulk_create() would be faster I think. See: http://vincent.is/speeding-up-django-postgres/  and https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
    
    # Bulk create is actually slightly slower than adding record by record
    d = Dependency(study_table=table_name, driver=driver_gene, target=target_gene, wilcox_p=row[2], effect_size=effect_size, histotype=histotype, mutation_type=mutation_type, study=study)
    # As inhibitors is a ManyToMany field so can't just assign it with: inhibitors=None, 
    # if not d.is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
    dependencies.append( d )

    # Fetch the boxplot:
    if FETCH_BOXPLOTS:
        fetch_boxplot_file(driver_gene, target_gene, histotype, isAchilles=False, isColt=False)    

    print("\r",count_added, end=" ")
    count_added += 1
  
  print( "%d dependency rows were added to the database" %(count_added))
  print( "%d dependency rows were skipped as wilcox_p > 0.05" %(count_skipped))
  print("Bulk_create ....")  
  Dependency.objects.bulk_create(dependencies) # Comparisons for Postgres:  http://stefano.dissegna.me/django-pg-bulk-insert.html
  print("Finished importing table.")


def add_counts_of_study_tissue_and_target_to_drivers():
  print("Adding study, tissue and target counts to drivers")
  # select driver, count(distinct study), count(distinct histotype), count(distinct target) from gendep_dependency group by driver;
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
        g.driver_num_studies = row['num_studies']
        g.driver_num_histotypes = row['num_histotypes']
        g.driver_num_targets = row['num_targets']
        g.save()
    except ObjectDoesNotExist: # Not found by the objects.get()
      print("*** ERROR: driver gene_name % NOT found in the Gene table: '%s'" %(row['driver']))
  print("Finished adding study, tissue and target counts to the drivers in the dependency table")

def add_counts_of_driver_tissue_and_target_to_studies(colt_pmid, colt_num_tissues):
  print("Adding driver, tissue and target counts to studies")
  # select study, count(distinct driver), count(distinct histotype), count(distinct target) from gendep_dependency group by study;
  counts = Dependency.objects.values('study').annotate( num_drivers=Count('driver', distinct=True), num_histotypes=Count('histotype', distinct=True), num_targets=Count('target', distinct=True) )
  # There is probably a faster SQL type quesry, or bulk_update
  for row in counts:
    try:
      print("study: %s %d %d %d" %(row['study'], row['num_drivers'], row['num_histotypes'], row['num_targets']))
      
      s = Study.objects.get(pmid=row['study'])  # .study_pmid
            
      # Double-check that name is same:
      if s.pmid != row['study']:
        print("*** ERROR: count study mismatch for '%s' and '%s'" %(s.pmid,row['study']))
      else:
        if s.pmid == colt_pmid:
           s.num_targets = colt_study_num_tissues
           print("But setting num_studies=%d (instead of %d) for Colt study (pmid=%s) as that is actual number tested in the study" %(colt_study_num_tissues,row['num_targets'],colt_pmid))
        else:
           s.num_targets = row['num_targets']
        s.num_drivers = row['num_drivers']
        s.num_histotypes = row['num_histotypes']

        s.save()
    except ObjectDoesNotExist: # Not found by the objects.get()
      print("*** ERROR: study pmid % NOT found in the Study table: '%s'" %(row['study']))
  print("Finished adding driver, tissue and target counts to the study table")


def read_achilles_R_results(result_file, table_name, study, study_old_pmid, tissue_type, isAchilles=True, isColt=True):
  global FETCH_BOXPLOTS, ACHILLES_FETCH_BOXPLOTS, COLT_FETCH_BOXPLOTS
  if isAchilles and isColt: print("*** ERROR: Cannot be both Achilles and Colt ******")

  print("\nImporting table: ",result_file)

  if isAchilles: print("ACHILLES FETCH_BOXPLOTS is: ",ACHILLES_FETCH_BOXPLOTS)
  elif isColt:   print("COLT FETCH_BOXPLOTS is: ",COLT_FETCH_BOXPLOTS)
  else:          print("FETCH_BOXPLOTS is: ",FETCH_BOXPLOTS)
  
  target_dict = dict()  # To find and replace any dependecies thart have different wilcox_p, just keeping the dependency with the lowest wilcox_p value.
  
  dataReader = csv.reader(open(result_file), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')

  # The file format for bytissues is: (the pancan doesn't have the 'tissue' column)
  # marker  target  nA      nB      wilcox.p        CLES    tissue
  # MYC_4609_ENSG00000136997        A2ML11_ENSG00000166535  5       7       0.946969696969697       0.228571428571429       BREAST
  # MYC_4609_ENSG00000136997        AADAC1_ENSG00000114771  5       7       0.734848484848485       0.4     BREAST

  count_skipped = 0
  count_added = 0
  count_replaced = 0
  count_not_replaced = 0
  dependencies = []

  row = next(dataReader) # To read the first heading line.
  header_dict = dict() # The column name to number for the above HGNC dict. 
  for i in range(len(row)): header_dict[row[i]] = i       # Store column numbers for each header item
  if row[0] != 'marker': print("***ERROR: Expected header to start with 'marker', but found:",row)
  idriver = header_dict['marker']
  itarget = header_dict['target']
  iwilcox = header_dict['wilcox.p'] # should be 16 if zero based
  ieffect_size = header_dict['CLES'] # CLES = 'common language effect size'
  # Added: zA     zB    ZDiff
  iza = header_dict['za']
  izb = header_dict['zb']
  izdiff = header_dict['zdiff']
  itissue = header_dict.get('tissue', -1) # The pancan file has no tissue column.        
  
  for row in dataReader:      
    # As per Colm's email 17-March-2016: "I would suggest we start storing dependencies only if they have p<0.05 AND CLES >= 0.65. "
    
    # Convert to numbers:
    # print(row)
    # print(row[idriver], row[itarget], row[iwilcox], row[ieffect_size])    
    row[iwilcox] = float(row[iwilcox])
    row[ieffect_size] = float(row[ieffect_size])
    
    if row[iwilcox] > 0.05 or row[ieffect_size] < 0.65:
      count_skipped += 1
      continue  # Skip as either the wilcox_p value or effect_size isn't significant

    # Added: zA     zB    ZDiff
    row[iza] = float(row[iza])
    row[izb] = float(row[izb])
    row[izdiff] = float(row[izdiff])    
      
    names = split_driver_gene_name(row[idriver])
    # driver_variant = names[0][-1:] # Seems we can ignore the driver variant as is trimming MYC to MY
    # if driver_variant not in ['1','2','3','4','5']: print("Unexpected driver_variant %s for %s" %(driver_variant,names[0])) 
    # names[0] = names[0][:-1]

    driver_gene = find_or_add_gene(names, is_driver=True, is_target=False, isAchilles=isAchilles, isColt=isColt)

    names = split_target_gene_name(row[itarget], isColt)
    target_variant = ''
    if isAchilles:
        target_variant = names[0][-1:]  # As target variant is single integer after target gene name in my formatted Achilles target names.
        names[0] = names[0][:-1]
    
    target_gene = find_or_add_gene(names, is_driver=False, is_target=True, isAchilles=isAchilles, isColt=isColt)
        
    # If using Histotype table: histotype = find_or_add_histotype(row[3], full_name=None)  # was: if row[3] not in histotypes: histotypes.append(row[3])
    if tissue_type=='PANCAN': histotype = 'PANCAN' 
    elif tissue_type=='BYTISSUE' and itissue!=-1:
        histotype = row[itissue]   # As using CharField(choices=...) and now is validated in the model.
        if histotype == "BONE": histotype = "OSTEOSARCOMA" # As in the Cambell(2016) R results this is called BONE, but converted to "OSTEOSARCOMA" in Tables S1K
    else: print("Invalid tissue_type='%s' or itissue=%d" %(tissue_type,itissue))
    
    mutation_type='Both'  # Default to 'Both' for current data now.

    # Using bulk_create() would be faster I think. See: http://vincent.is/speeding-up-django-postgres/  and https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
    
    # Bulk create is actually slightly slower than adding record by record in SQLite, but in MySQL it will be faster

    key = driver_gene.gene_name + '_' + target_gene.gene_name + ' ' + histotype + '_' + study.pmid # Could maybe use the gene object id as key ?
    d = target_dict.get(key,None)
    if d is not None:
        if not isAchilles: print("*** ERROR: The driver + target + histotype + study key '%s' should be unique for non-Achilles data" %(key))
        if row[iwilcox] < d.wilcox_p:
            if d.study_table != table_name: 
                print("d.study_table(%s) != table_name(%s)" %(d.study_table, table_name))
            if d.mutation_type != mutation_type:
                print("d.mutation_type(%s) != mutation_type(%s)" %(d.mutation_type, mutation_type))
            d.wilcox_p = row[iwilcox]
            d.effect_size = row[ieffect_size]
            # Added: zA     zB    ZDiff
            d.za = row[iza]
            d.zb = row[izb]
            d.zdiff = row[izdiff]
            if d.target_variant == target_variant: print("** ERRROR: target_variant already in database for target_variant '%s' and key: '%s'" %(target_variant,key))
            d.target_variant = target_variant # Need to update the target_variant, as it is needed to retrieve the correct boxplot from the R boxplots, where image file is: driver_gene_target_gene+target_variant_histotype_Pmid.png
            count_replaced += 1
        else:
            count_not_replaced += 1        
    else:
        # Added: zA     zB    ZDiff
        d = Dependency(study_table=table_name, driver=driver_gene, target=target_gene, target_variant=target_variant, wilcox_p=row[iwilcox], effect_size=row[ieffect_size], za = row[iza], zb = row[izb], zdiff = row[izdiff], histotype=histotype, mutation_type=mutation_type, study=study)
        # As inhibitors is a ManyToMany field so can't just assign it with: inhibitors=None, 
        # if not d.is_valid_histotype(histotype): print("**** ERROR: Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
        dependencies.append( d )
        target_dict[key] = d

    print("\r",count_added, end=" ")
    count_added += 1
    
  # Now fetch the boxplots for those added:
  count_boxplots = 0
  if (isAchilles and ACHILLES_FETCH_BOXPLOTS) or (isColt and COLT_FETCH_BOXPLOTS) or ((not isAchilles and not isColt) and FETCH_BOXPLOTS) :
     for d in dependencies:
        fetch_boxplot_file(d.driver, d.target, d.histotype, isAchilles=isAchilles, isColt=isColt, target_variant=d.target_variant)
        count_boxplots += 1
        
  print( "%d dependency rows were added to the database, %d replaced and %d not replaced, so %d target_variants" %(count_added,count_replaced, count_not_replaced, count_replaced+count_not_replaced))
  print( "%d dependency rows were skipped as wilcox_p > 0.05 or effect_size < 0.65" %(count_skipped))
  print( "%d boxplot images were fetched" %(count_boxplots))
  print("Bulk_create dependencies ....")
  Dependency.objects.bulk_create(dependencies) # Comparisons for Postgres:  http://stefano.dissegna.me/django-pg-bulk-insert.html
  print("Finished importing table.")


# Achilles data:  
# Pan-cancer:
#  113,970 dependency rows were skipped as wilcox_p > 0.05 or effect_size < 0.65
#   5,940 dependency rows were added to the database, (15 replaced and 56 not replaced, so 71 target_variants)

# By tissue:
#  289,592 dependency rows were skipped as wilcox_p > 0.05 or effect_size < 0.65
#   12,807 dependency rows were added to the database, (12 replaced and 68 not replaced, so 80 target_variants)


"""
# Columns are:
(0+1)   marker
(1+1)   target
(2+1)   nA
(3+1)   nB
(4+1)   sensitive.threshold
(5+1)   med.grpA
(6+1)   med.grpB
(7+1)   med.grpA-med.grpB
(8+1)   count.grpA.sens
(9+1)   count.grpB.sens
(10+1)  percent.grpA.sens
(11+1)  percent.grpB.sens
(12+1)  min.grpA
(13+1)  min.grpB
(14+1)  spearman.r
(15+1)  spearman.p
(16+1)  wilcox.p
(17+1)  mptest.p
(18+1)  tissue  <-- Only in the bytissue file!

Line format is:

marker  target  nA      nB      sensitive.threshold     med.grpA        med.grpB        med.grpA-med.grpB       count.grpA.sens count.grpB.sens percent.grpA.sens       percent.grpB.sens       min.grpA        min.grpB    spearman.r      spearman.p      wilcox.p        mptest.p
MYC_4609_ENSG00000136997        A2ML11_ENSG00000166535  39      95      -1.82415217849227       0.298448693314915       -0.0271821540880284     0.325630847402943       0       2       0       2.10526315789474   -1.3856690863059 -1.99033140631124       0.221916761978561       0.995017211587167       0.994792207576161       NA
....

The bytissue resuilt shave an extra 'tissue' column at the end of each row:
marker  target  nA      nB      sensitive.threshold     med.grpA        med.grpB        med.grpA-med.grpB       count.grpA.sens count.grpB.sens percent.grpA.sens       percent.grpB.sens       min.grpA        min.grpB        spearman.r      spearman.p      wilcox.p        mptest.p        tissue
MYC_4609_ENSG00000136997        A2ML11_ENSG00000166535  5       7       -1.82415217849227       0.804801172130142       -0.0271821540880284     0.83198332621817        0       0       0       0       -1.3856690863059        -0.431582700695377      0.465170523984072       0.936225670531354       0.946969696969697       NA      BREAST
....
"""
   

def add_tissue_and_study_lists_for_each_driver():
    print("Adding tissue list to each driver")
    # For setting the tissue menu after user selects gene of interest:
    # for 
    # http://joelsaupe.com/programming/order-distinct-values-django/
    # Doesn't work: q = Dependency.objects.only('driver_id','histotype').annotate().order_by('driver_id')
    # print(q.query)
   
    q = Dependency.objects.order_by('driver_id').values('driver_id','histotype').distinct() # putting order_by() after distinct() might not work correctly.
    # print(q.query)
    driver_tissues = dict()
    for d in q:
        # print(d)
        driver = d['driver_id']
        if driver in driver_tissues:
            driver_tissues[driver] += ';'+d['histotype']
        else:
            driver_tissues[driver] = d['histotype']
            
    with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()    
      for driver in driver_tissues:
        # try:
        g = Gene.objects.get(gene_name=driver)        
        g.driver_histotype_list = driver_tissues[driver]
        num_in_list = g.driver_histotype_list.count(';')+1
        if g.driver_num_histotypes != num_in_list:   # BUT 'g.num_histotypes' could drefer to targets not drivers.
            print("Count mismatch: g.num_histotypes(%d) != num_in_list(%d)" %(g.driver_num_histotypes,num_in_list))
        g.save()
        print(g.gene_name,g.driver_histotype_list);
        # except ObjectDoesNotExist: # Not found by the objects.get()

    q = Dependency.objects.order_by('driver_id').values('driver_id','study_id').distinct() # putting order_by() after distinct() might not work correctly.
    #print(q.query)
    driver_studies = dict()
    for d in q:
        # print(d)
        driver = d['driver_id']
        if driver in driver_studies:
            driver_studies[driver] += ';'+d['study_id']
        else:
            driver_studies[driver] = d['study_id']
            
    with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()        
      for driver in driver_studies:
        # try:
        g = Gene.objects.get(gene_name=driver)
        g.driver_study_list = driver_studies[driver]
        num_in_list = g.driver_study_list.count(';')+1
        if g.driver_num_studies != num_in_list:   # BUT 'g.num_studies' could drefer to targets not drivers.
            print("Count mismatch: g.num_studies(%d) != num_in_list(%d)" %(g.driver_num_studies,num_in_list))
        g.save()
        print(g.gene_name,g.driver_study_list);        
        # except ObjectDoesNotExist: # Not found by the objects.get()
        
    print("Finished adding tissue and study lists to drivers")
   
   # Dependency.objects.order_by('driver_id').values('driver_id','histotype').distinct() # putting order_by() after distinct() won't work correctly.
   # q = ProductOrder.objects.values('Category').distinct()
   
   #ProductOrder.objects.order_by('category').values_list('category', flat=True).distinct()
   
# print q.query # See for yourself.

"""

"ARID1A"
"CCND1"
"CDKN2A"
"EGFR"
"ERBB2"
"GNAS"
"KRAS"
"MAP2K4"
"MDM2"
"MYC"
"NF1"
"PIK3CA"
"PTEN"
"RB1"
"SMAD4"
"TP53"

	"CCND1_595_ENSG00000110092", - 
	"CDKN2A_1029_ENSG00000147889", - 
	"EGFR_1956_ENSG00000146648", - 
	"ERBB2_2064_ENSG00000141736", - 
	"GNAS_2778_ENSG00000087460", - 
	"KRAS_3845_ENSG00000133703", - 
	"SMAD4_4089_ENSG00000141646", - 
	"MDM2_4193_ENSG00000135679", -
	"MYC_4609_ENSG00000136997", -
	"NF1_4763_ENSG00000196712", - 
	"NOTCH2_4853_ENSG00000134250", **
	"NRAS_4893_ENSG00000213281", **
	"PIK3CA_5290_ENSG00000121879", - 
	"PTEN_5728_ENSG00000171862", - 
	"RB1_5925_ENSG00000139687", - 
	"MAP2K4_6416_ENSG00000065559", - 
	"SMARCA4_6597_ENSG00000127616", **
	"STK11_6794_ENSG00000118046", **
	"TP53_7157_ENSG00000141510", - 
	"ARID1A_8289_ENSG00000117713", -
	"FBXW7_55294_ENSG00000109670" **
    
    Not in Colt data:
    NOTCH2_4853_ENSG00000134250,
	NRAS_4893_ENSG00000213281,
	SMARCA4_6597_ENSG00000127616,
	STK11_6794_ENSG00000118046,
	FBXW7_55294_ENSG00000109670
"""
    

def unmark_drivers_not_in_the_21genes():
  # SJB - list copied from the "run_intercell_analysis.R" downloaded from github GeneFunctionTeam repo on 12 March 2016
  # Define the set of 21 genes with good represention (≥ 7 mutants).
  # This list can be used to filter the complete set of tests
  # cgc_vogel_genes_with_n7 
  the21drivers = [
	"CCND1",   # _595_ENSG00000110092",
	"CDKN2A",  # _1029_ENSG00000147889",
	"EGFR",    # _1956_ENSG00000146648",
	"ERBB2",   # _2064_ENSG00000141736",
	"GNAS",    # _2778_ENSG00000087460",
	"KRAS",    # _3845_ENSG00000133703",
	"SMAD4",   # _4089_ENSG00000141646",
	"MDM2",    # _4193_ENSG00000135679",
	"MYC",     # _4609_ENSG00000136997",
	"NF1",     # _4763_ENSG00000196712",
	"NOTCH2",  # _4853_ENSG00000134250",
	"NRAS",    # _4893_ENSG00000213281",
	"PIK3CA",  # _5290_ENSG00000121879",
	"PTEN",    # _5728_ENSG00000171862",
	"RB1",     # _5925_ENSG00000139687",
	"MAP2K4",  # _6416_ENSG00000065559",
	"SMARCA4", # _6597_ENSG00000127616",
	"STK11",   # _6794_ENSG00000118046",
	"TP53",    # _7157_ENSG00000141510",
	"ARID1A",  # _8289_ENSG00000117713",
	"FBXW7",   # _55294_ENSG00000109670"
    "BRAF",    # _673_ENSG00000157764",  # Added BRAF on 14 April 2016 for future runs
	"CDH1",    # _999_ENSG00000039068"   # Added CDH1 on 15 April 2016 for future runs
	]
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
    for g in Gene.objects.all().iterator():
       if g.is_driver:
          if g.gene_name not in the21drivers:
            print("Driver not in the 21 list:",g.gene_name)
            g.is_driver = False
            g.save()

  print("Finished unmarking drivers that are not in the list of 21 drivers")

  



if __name__ == "__main__":
# add_tissue_and_study_lists_for_each_driver()

  unmark_drivers_not_in_the_21genes()
  
  #add_counts_of_driver_tissue_and_target_to_studies()
  #sys.exit()
  #exit()

if __name__ == "__sjb_ignore_these__":  
  # global static_gendep_boxplot_dir As this isn't a def then don't need global here.
  if static_gendep_boxplot_dir is None or static_gendep_boxplot_dir == '':
     print("****** WARNING: static_gendep_boxplot_dir is empty ******")
     static_gendep_boxplot_dir = "gendep/static/gendep/boxplots"
     # exit()
     
  make_AtoZ_subdirs(static_gendep_boxplot_dir)
  
  load_hgnc_dictionary()
  load_mygene_hgnc_dictionary()
  
  # ============================================================================================
  Campbell_study_pmid = "26947069"
  study_old_pmid = "nnnnnnnn" # This is  the ID assigned to boxplots by the R script at present, but can change this in future to be same as the actual pmid.
  study_old_pmid = "26947069"
  study_code = "B" # 'B' for campBell
  study_short_name = "Campbell(2016)"
  study_title = "Large Scale Profiling of Kinase Dependencies in Cancer Cell Line"
  study_authors = "Campbell J, Colm JR, Brough R, Bajrami I, Pemberton H, Chong I, Costa-Cabral S, Frankum J, Gulati A, Holme H, Miller R, Postel-Vinay S, Rafiq R, Wei W, Williamson CT, Quigley DA, Tym J, Al-Lazikani B, Fenton T, Natrajan R, Strauss S, Ashworth A, Lord CJ"
  study_abstract = "One approach to identifying cancer-specific vulnerabilities and novel therapeutic targets is to profile genetic dependencies in cancer cell lines. Here we use siRNA screening to estimate the genetic dependencies on 714 kinase and kinase-related genes in 117 different tumor cell lines. We provide this dataset as a resource and show that by integrating siRNA data with molecular profiling data, such as exome sequencing, candidate genetic dependencies associated with the mutation of specific cancer driver genescan be identified. By integrating the identified dependencies with interaction datasets, we demonstrate that the kinase dependencies associated with many cancer driver genes form dense connections on functional interaction networks. Finally, we show how this resource may be used to make predictions about the drug sensitivity of genetically or histologically defined subsets of cell lines, including an increased sensitivity of osteosarcoma cell lines to FGFR inhibitors and SMAD4 mutant tumor cells to mitotic inhibitors."
  study_summary = "siRNA screen of 714 kinase and kinase-related genes in 117 different tumor cell lines"
  study_experiment_type = "kinome siRNA"
  study_journal = "Cell reports"
  study_pub_date = "2016, 2 Mar"
 
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()
    # Before using atomic(), I tried "transaction.set_autocommit(False)" but got error "Your database backend doesn't behave properly when autocommit is off."
    print("\nEmptying database tables")
    for table in (Dependency, Study, Gene, Drug): table.objects.all().delete()  # removed: Histotype,

    study=add_study( Campbell_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date)
  
    #for table_name in ('S1I', 'S1K'):
    #  csv_filepathname=os.path.join(PROJECT_DIR, os.path.join('input_data', 'Table_'+table_name+'_min_cols.txt'))   # Full path and name to the csv file
    #  import_data_from_tsv_table(csv_filepathname, table_name, study, study_old_pmid)
  # transaction.commit() # just needed if used "transaction.set_autocommit(False)"

    # BUT NEED to FIX THE
    table_name ='S1I'
    Cambell_results_pancan = "univariate_results_v26_pancan_kinome_combmuts_28April2016_witheffectsize.txt"
    csv_filepathname=os.path.join(analysis_dir, Cambell_results_pancan)
    read_achilles_R_results(csv_filepathname, table_name, study, study_old_pmid, tissue_type='PANCAN', isAchilles=False, isColt=False)

    table_name = 'S1K'
    Cambell_results_bytissue = "univariate_results_v26_bytissue_kinome_combmuts_28April2016_witheffectsize.txt"
    csv_filepathname=os.path.join(analysis_dir, Cambell_results_bytissue)
    read_achilles_R_results(csv_filepathname, table_name, study, study_old_pmid, tissue_type='BYTISSUE', isAchilles=False, isColt=False)

    Campbell_study_num_tissues = 
    # *** NOTE, warnings from R:
    # There were 50 or more warnings (use warnings() to see the first 50)

    # 44: In wilcox.test.default(zscores[grpA, j], zscores[grpB,  ... :
    # cannot compute exact p-value with ties

    # ============================================================================================
    # Project Achilles: # https://www.broadinstitute.org/achilles  and http://www.nature.com/articles/sdata201435
    Achilles_study_pmid     = "25984343"
    study_old_pmid = "25984343"
    study_code = "A" # 'A' for Achilles
    study_short_name = "Cowley(2014)"
    study_title = "Parallel genome-scale loss of function screens in 216 cancer cell lines for the identification of context-specific genetic dependencies."
    study_authors = "Cowley GS, Weir BA, Vazquez F, Tamayo P, Scott JA, Rusin S, East-Seletsky A, Ali LD, Gerath WF, Pantel SE, Lizotte PH, Jiang G, Hsiao J, Tsherniak A, Dwinell E, Aoyama S, Okamoto M, Harrington W, Gelfand E, Green TM, Tomko MJ, Gopal S, Wong TC, Li H, Howell S, Stransky N, Liefeld T, Jang D, Bistline J, Hill Meyers B, Armstrong SA, Anderson KC, Stegmaier K, Reich M, Pellman D, Boehm JS, Mesirov JP, Golub TR, Root DE, Hahn WC"
    study_abstract = "Using a genome-scale, lentivirally delivered shRNA library, we performed massively parallel pooled shRNA screens in 216 cancer cell lines to identify genes that are required for cell proliferation and/or viability. Cell line dependencies on 11,000 genes were interrogated by 5 shRNAs per gene. The proliferation effect of each shRNA in each cell line was assessed by transducing a population of 11M cells with one shRNA-virus per cell and determining the relative enrichment or depletion of each of the 54,000 shRNAs after 16 population doublings using Next Generation Sequencing. All the cell lines were screened using standardized conditions to best assess differential genetic dependencies across cell lines. When combined with genomic characterization of these cell lines, this dataset facilitates the linkage of genetic dependencies with specific cellular contexts (e.g., gene mutations or cell lineage). To enable such comparisons, we developed and provided a bioinformatics tool to identify linear and nonlinear correlations between these features."
    study_summary = "shRNA screen of 11,000 genes in 216 different cancer cell lines, with 5 shRNAs per gene"
    study_experiment_type = "genome shRNA"
    study_journal = "Scientific Data"
    study_pub_date = "2014, 30 Sep"
    study=add_study( Achilles_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date )

    #Achilles_results_pancan = "univariate_results_Achilles_v2_for21drivers_pancan_kinome_combmuts_160312_preeffectsize.txt"
    table_name = ''
    Achilles_results_pancan ="univariate_results_Achilles_v2_for21drivers_pancan_kinome_combmuts_180312_witheffectsize.txt"
    csv_filepathname=os.path.join(analysis_dir, Achilles_results_pancan)
    read_achilles_R_results(csv_filepathname, table_name, study, study_old_pmid, tissue_type='PANCAN', isAchilles=True, isColt=False)
    
    #Achilles_results_bytissue = "univariate_results_Achilles_v2_for21drivers_bytissue_kinome_combmuts_160312_preeffectsize.txt"
    table_name = ''
    Achilles_results_bytissue ="univariate_results_Achilles_v2_for21drivers_bytissue_kinome_combmuts_180312_witheffectsize.txt"
    csv_filepathname=os.path.join(analysis_dir, Achilles_results_bytissue)
    read_achilles_R_results(csv_filepathname, table_name, study, study_old_pmid, tissue_type='BYTISSUE', isAchilles=True, isColt=False)

    Achilles_study_num_tissues = 
    
    #** Maybe my browser memory?
    #https://www.ncbi.nlm.nih.gov/pubmed/
    #Bad Request

    #Your browser sent a request that this server could not understand.
    #Size of a request header field exceeds server limit.
    #Cookie
    #/n

    # ==================================================================================================
    # Colt:  https://neellab.github.io/bfg/   https://www.ncbi.nlm.nih.gov/pubmed/26771497
   
    Colt_study_pmid     = "26771497"
    study_old_pmid = "26771497"
    study_code = "C"  # 'C' for Colt
    study_short_name = "Marcotte(2016)"
    study_title = "Functional Genomic Landscape of Human Breast Cancer Drivers, Vulnerabilities, and Resistance."
    study_authors = "Marcotte R, Sayad A, Brown KR, Sanchez-Garcia F, Reimand J, Haider M, Virtanen C, Bradner JE, Bader GD, Mills GB, Pe'er D, Moffat J, Neel BG"
    study_abstract = "Large-scale genomic studies have identified multiple somatic aberrations in breast cancer, including copy number alterations and point mutations. Still, identifying causal variants and emergent vulnerabilities that arise as a consequence of genetic alterations remain major challenges. We performed whole-genome small hairpin RNA (shRNA) \"dropout screens\" on 77 breast cancer cell lines. Using a hierarchical linear regression algorithm to score our screen results and integrate them with accompanying detailed genetic and proteomic information, we identify vulnerabilities in breast cancer, including candidate \"drivers,\" and reveal general functional genomic properties of cancer cells. Comparisons of gene essentiality with drug sensitivity data suggest potential resistance mechanisms, effects of existing anti-cancer drugs, and opportunities for combination therapy. Finally, we demonstrate the utility of this large dataset by identifying BRD4 as a potential target in luminal breast cancer and PIK3CA mutations as a resistance determinant for BET-inhibitors."
    study_summary = "shRNA screen of on 77 breast cancer cell lines. Dropout trends for each screen in at three time points (8-9 arrays per screen, and a total of 621 arrays)"
    study_experiment_type = "genome shRNA"
    study_journal = "Cell"
    study_pub_date = "2016, 14 Jan"
    study=add_study( Colt_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date )

    # Colt_results_pancan = "NONE" - as Colt is only Breast tissue
    table_name = ''
    Colt_results_bytissue = "univariate_results_Colt_v1_bytissue_kinome_combmuts_12April2016_witheffectsize.txt"
    
    csv_filepathname=os.path.join(analysis_dir, Colt_results_bytissue)
    read_achilles_R_results(csv_filepathname, table_name, study, study_old_pmid, tissue_type='BYTISSUE', isAchilles=False, isColt=True)

    Colt_study_num_tissues = 15697 # The actual number of tisses tested in the Colt (Marcotte et al) study, although only 8,898 dependencies are in the dependency table, as rest don't meet the (p<=0.05 and effect_size>=0.65) requirtement.
    
    # I downloaded: https://neellab.github.io/bfg/
    # "updated shRNA annotations: Update to Entrez gene ids and symbols, to account for changed symbols, deprecated Entrez ids and the like. Approximately 300 gene ids from the original TRC II annotations no longer exist, leading to a slightly reduced overall gene id and shRNA count."
    
    # ============================================================================================
    add_counts_of_study_tissue_and_target_to_drivers()
    #### ***** and add counts of num_drivers 
    add_counts_of_driver_tissue_and_target_to_studies(colt_pmid=Colt_study_pmid, colt_num_tissues=Colt_study_num_tissues)
    
    add_tissue_and_study_lists_for_each_driver()