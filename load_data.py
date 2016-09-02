#!/usr/bin/env python

#### Todo: Remove the globabls from read HGNC, etc....

# The Windows 'py' launcher should also recognise the above shebang line.

""" Script to import the data into the database tables """
# NOTES:
# (1) An alternative for loading data into empty database is using 'Fixtures', however this data seems to complex for fixtures: https://docs.djangoproject.com/en/1.9/howto/initial-data/
# or django-adapters: http://stackoverflow.com/questions/14504585/good-ways-to-import-data-into-django
#                     http://django-adaptors.readthedocs.org/en/latest/

# (2) No longer using the Achilles target variants - as only keeping the variant with the lowest (ie. best) p-value.
# (3) No longer fetching the boxplot png files, as using the boxplot text data to plot SVG in webbrowser.
# (4) Do the annotation with entrez, ensembl, etc as a separate script later.
# (5) Add the ensembl_protein - as is used by StringDB for interactions.


import sys, os, csv, re
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count # For the distinct study and target counts for drivers.

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")

# Needs the following django.setup(), otherwise get exception about: "django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet."
# This django.setup() is called in the 'execute_from_command_line(sys.argv)' in the manage.py script, eg. when migarting adtabase tables.
import django
django.setup()

from gendep.models import Study, Gene, Dependency  # Removed: Histotype, Drug, Comment

# In the SQLite database (used for development locally), the max_length parameter for fields is ignored as the "numeric arguments in parentheses that following the type name (ex: "VARCHAR(255)") are ignored by SQLite - SQLite does not impose any length restrictions (other than the large global SQLITE_MAX_LENGTH limit) on the length of strings, ...." (unless use sqlites CHECK contraint option)

### BUT MySQL does enforce max_length, so MySQL will truncate strings that are too long, (including keys so loss of unique primary key) so need to check for data truncation, as it jsut gives a warning NOT an exception.
import warnings # To convert the MySQL data truncation (due to field max_length being too small) into raising an exception:
warnings.filterwarnings('error', 'Data truncated .*') # regular expression to catch: Warning: Data truncated for column 'gene_name' at row 1

# HGNC input file used by load_hgnc_dictionary(hgnc_infile):
hgnc_infile = os.path.join('input_data','hgnc_complete_set.txt')

entrez_gene_full_details_for_Achilles_and_Colt_infile = "entrez_gene_full_details_all_Achilles_and_Colt_and_driversCampbell_sorted_unique.txt"

# The alteration (eg. mutation, copy number) considered for each driver - to be loaded into the Gene table for each driver:
driver_alteration_details_file = os.path.join('input_data','AlterationDetails.csv')



# Set flag to output the info messages. On command-line can use '>' redirect output these to a text file.
INFO_MESSAGES = True

def info(message):
    if (INFO_MESSAGES):
        print('INFO: %s\n' % message)

def debug(message):
    print('DEBUG: %s\n' % message)
    
def warn(message):
	sys.stderr.write('* WARNING:  %s\n' % message)

def warning(message):
	warn(message)
    
def error(message):
	sys.stderr.write('*** ERROR:  %s\n' % message)
        
def fatal_error(message, code=1):
	sys.stderr.write('***** ERROR:  %s\n' % message)
	sys.exit(code)
    # or: raise RuntimeError(message)


def find_or_add_study(pmid, code, short_name, title, authors, abstract, summary, experiment_type, journal, pub_date):
  """ Finds or adds study in the Study table """
  s, created = Study.objects.get_or_create( pmid=pmid, defaults={'code': code, 'short_name': short_name, 'title': title, 'authors': authors, 'abstract': abstract, 'summary': summary, 'experiment_type': experiment_type, 'journal': journal, 'pub_date': pub_date} )
  return s


def find_or_add_histotype(histotype, full_name):
  """ This function is needed if return to using the Histotype table, rather than the current choices list """
  # If using Histotype table:
  # if full_name is None: full_name={'PANCAN':'Pan cancer'}.get(histotype, histotype.title()) # The other known types are: 'BREAST', 'OSTEOSARCOMA', 'OESOPHAGUS', 'LUNG', and 'OVARY'
  # h, created = Histotype.objects.get_or_create(histotype=histotype, defaults={'full_name': full_name} )

  # As using the HISTOTYPE_CHOICES list in the Dependency class (instead of a Histotype table):
  if Dependency.is_valid_histotype(histotype):    
      h = histotype
  else:
      error("Histotype %s NOT found in HISTOTYPE_CHOICES list: %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
      h = None

  return h


driver_name_warning_already_reported = dict() # To reduce multiple duplicate messages during loading of driver genes.
def split_driver_gene_name(long_name):
  """ Splits a Driver name from format "genename_entrezid_ensemblid" (eg: CCND1_595_ENSG00000110092 ), as output by the R function "write.table(uv_results_kinome_combmuts_bytissue, ....." in the "run_intercell_analysis.R" script, into the three separate parts 
  
    parameter 'long_name' is the input name, eg: "CCND1_595_ENSG00000110092"
    
  Output is names[3] list of [ genename, entrezid, ensemblid ] eg: [ "CCND1", "595", "ENSG00000110092" ]
  
  In the data from R, there are drivers with two or more ensembl gane names, so will just use the first ensembl name:
  
    EIF1AX_101060318_ENSG00000173674_ENSG00000198692
    HIST1H3B_3020_ENSG00000132475_ENSG00000163041
    TRIM48_101930235_ENSG00000150244_ENSG00000223417
    RGPD3_653489_ENSG00000015568_ENSG00000153165_ENSG00000183054
    MEF2BNB.MEF2B_729991_ENSG00000064489_ENSG00000254901
    HIST1H2BF_8347_ENSG00000168242_ENSG00000180596_ENSG00000187990_ENSG00000197697_ENSG00000197846
    NUTM2F_441457_ENSG00000130950_ENSG00000188152
    H3F3B_3021_ENSG00000132475_ENSG00000163041
    WDR33_84826_ENSG00000136709_ENSG00000173349
    KRTAP4.11_728224_ENSG00000204880_ENSG00000212721
  """
  names = long_name.split('_') 
  if len(names)!=3 and long_name not in driver_name_warning_already_reported:
      error("Invalid number of parts in driver gene, (as expected 3 parts): '%s'" %(long_name))
      driver_name_warning_already_reported[long_name] = None # Storing 'None' can be more memory efficient than 'True'
  if not names[1].isdigit() and long_name not in driver_name_warning_already_reported:
      error("Expected integer for Entrez id second part of name: '%s'"  %(long_name))
      driver_name_warning_already_reported[long_name] = None
  if names[2][:4] != 'ENSG' and names[2]!='NoEnsemblIdFound' and long_name not in driver_name_warning_already_reported:
      error("Expected 'ENSG' for start of driver ensembl name: '%s'" %(long_name))
      driver_name_warning_already_reported[long_name] = None
      
  return names


target_name_warning_already_reported = dict()  # To reduce multiple duplicate messages during loading of target genes.
def split_target_gene_name(long_name, isAchilles, isColt):
  """ Splits a Target name read from output of the R function "write.table(uv_results_kinome_combmuts_bytissue, ....." in the "run_intercell_analysis.R" script.
:
      parameters:
        'long_name' - is the input name, eg: "DCK_ENSG00000156136" 
      
        isColt - to indicate this is Colt study name format, as Campbell and Achilles format is "genename_ensemblid" (eg: DCK_ENSG00000156136 ), whereas Colt format is "genename_entrezid" (eg: ATP1A1_476 )
        
      The long_name can be genename_NoEnsemblIdFound if data input to R did not find a correponding ensembl id.
      
    Output is a names[3] list of: of [ genename, "", ensemblid ] or [ genename, entrezid, "" ], so has same number of elements in names array for target names as in driver names (returned by function 'split_driver_gene_name' above.)
  """  
  
  names = long_name.split('_')

  if len(names)!=2:
    if names[0] == 'CDK12' and len(names)==3 and names[2]=='CRK7': # as "CDK12_ENSG00000167258_CRK7" is an exception to target format (CRK7 is an alternative name)
      names.pop()   # Remove the last 'CRK7' name from the names list
    elif names[0] == 'TRIM27' and len(names)==3 and names[2]=='RFP': # Another exception is: TRIM27_ENSG00000215641_RFP
      names.pop()   # Remove the last 'RFP' name from the names list      
    elif long_name not in target_name_warning_already_reported:
      warn("Invalid number of parts in target gene, (as expected 2 parts): '%s'" %(long_name))
      target_name_warning_already_reported[long_name] = None

  if isColt or isAchilles:
    names.append('') # As Colt and Achilles names have entrez id, but not ensembl id, so add empty "" at end of names list.  
  else:
    if names[1][:4] != 'ENSG' and names[1]!='NoEnsemblIdFound' and long_name not in target_name_warning_already_reported:
      error("Expected 'ENSG' for start of target ensembl name: '%s'" %(long_name))
      target_name_warning_already_reported[long_name] = None
      
    names.insert(1,'') # Insert empty entrezid to makes names[3] list
    
  return names



driver_alterations = dict()
def load_driver_alterations_dictionary():
  """ Reads the Driver Alterations into dictionary to add to the Gene table for each driver gene """
   
  dataReader = csv.reader(open(driver_alteration_details_file), dialect='excel') # as this input file is comma-separated (ie. CSV), not tab-separated.
     # or: dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  row = next(dataReader) # The header line.
  if row[0]!="Gene" or row[1]!="Alterations Considered":
      error("Unexpected header line in Driver alterations file: %s" %(row))
  
  for row in dataReader:
      driver_name = row[0]
      if driver_name in driver_alterations:
          error("Driver '%s' is in the Driver Alterations file more than once" %(driver_name))
          
      driver_alterations[driver_name] = row[1]      




entrez_info = dict()
entrez_info_gene_name_to_entrez = dict()
entrez_info_ensembl_to_entrez = dict()
entrez_secondary_ids = dict()
def load_entrez_gene_full_details_for_Achilles_and_Colt(infile):
  entrez_gene_full_details_Achilles_and_Colt = "entrez_gene_full_details_Achilles_and_Colt.txt"

  global ie_entrez,ie_status_string,ie_status_int,ie_current_entrez_id,ie_current_locus,ie_gene_name,ie_maploc,ie_hgnc,ie_ensembl_gene,ie_hprd,ie_omim,ie_vega,ie_ensembl_protein,ie_uniprot,ie_desc,ie_synonyms,ie_summary
  print("\nLoading Entrez Gene data from:",infile)

  dataReader = csv.reader(open(infile, encoding='utf-8'), dialect='excel-tab')
  # or: dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  row = next(dataReader)

  ie = dict() # The column name to number for the above entrez_info dict. 
  for i in range(len(row)): ie[row[i]] = i   # Store column numbers for each item in the input header line.
  
  ie_entrez  = ie["Entrez"]
  ie_status = ie["Status"]
  ie_status_int = ie["Status_int"]
  ie_current_entrez  = ie["Current_entrez"]
  ie_current_locus  = ie["Current_locus"]
  ie_gene_name  = ie["Gene_name"]
  ie_maploc   = ie["Maploc"]
  ie_hgnc  = ie["HGNC"]
  ie_ensembl_gene  = ie["Ensembl_gene"]
  ie_hprd  = ie["HPRD"]
  ie_omim = ie["OMIM"]
  ie_vega  = ie["VEGA"]
  ie_ensembl_protein  = ie["Ensembl_protein"]
  ie_uniprot  = ie["UniProt"]
  ie_desc  = ie["Desc"]              
  ie_synonyms = ie["Synonyms"]
  ie_summary = ie["Summary"]

  for row in dataReader:      
#    if row[ie_status_string] == 'discontinued':
#       continue  # So skip this entry.
       
    entrez = row[ie_entrez]
    if row[ie_current_entrez]!='' and row[ie_current_entrez] != entrez:
      warn("gene_track_entrez_id %s != current_entrez_id %s, status:%s" %(entrez,row[ie_current_entrez],row[ie_status]))
      if row[ie_status] == 'secondary':
        entrez_secondary_ids[entrez] = row[ie_current_entrez] # As Entrez_id has changed.
          
    if entrez in entrez_info:
      warn("Duplicated entrez_id in entrez_info: '%s' status='%s' in file: Entrez: '%s' '%s' \nrow: %s\nentrez_info: %s\n" %(entrez, row[ie_status], entrez_info[entrez][ie_entrez],entrez_info[entrez][ie_status],  row, entrez_info[entrez]) )
    entrez_info[entrez] = row # Store the whole row for simplicity.
    
    # Dictionaries to use to for the Campbell data which has gene_name and ensembl ids:
    entrez_info_gene_name_to_entrez[row[ie_gene_name]] = entrez
    if ';' in row[ie_ensembl_gene]:
      for each_ensembl_gene in row[ie_ensembl_gene].split(";"): entrez_info_ensembl_to_entrez[each_ensembl_gene] = entrez
    else:
      entrez_info_ensembl_to_entrez[row[ie_ensembl_gene]] = entrez
    
    """
    # Build dictionary of prev-names & synonyms to gene_names:
    # print("%s : prev_names=%s, synonyms=%s" %(gene_name,row[iprev_names],row[isynonyms]))    
    prevname_synonyms = row[iprev_names] + ('' if row[iprev_names]=='' or row[isynonyms]=='' else '|') + row[isynonyms]
    for key in prevname_synonyms.split('|'):
      if key == '': continue
      # print("  key:",key)
      if key in synonyms_to_hgnc:
        num_synonmys_already_exist += 1
        # print("**** ERROR: For gene %s Synonym %s already exists in gene %s:" %(gene_name,key,synonyms_to_hgnc[key]))
        synonyms_to_hgnc[key] += ';'+gene_name
        print("synonyms_to_hgnc[%s] = '%s'" %(key,synonyms_to_hgnc[key]))
      else:
        synonyms_to_hgnc[key] = gene_name
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])
    """
  




hgnc = dict() # To read the HGNC ids into a dictionary
#ihgnc = dict() # The column name to number for the above HGNC dict.
synonyms_to_hgnc = dict()
entrez_to_hgnc = dict() 
def load_hgnc_dictionary(hgnc_infile):
  """ Reads the HGNC gene ids into a dictionary to use for adding each gene's full_name, synomyns,  external ids to the Gene table """
  # Could use Pandas to read the csv file, but Pandas is an extra dependency to install. Eg: import pandas as pd;   data = pd.read_csv("names.csv", nrows=1)
  # Alternatively use a webservice, eg: http://www.genenames.org/help/rest-web-service-help
  
  global hgnc, isymbol, ifull_name, istatus, isynonyms, iprev_names, ientrez_id, iensembl_id, icosmic_id, iomim_id, iuniprot_id, ivega_id, ihgnc_id
  print("\nLoading HGNC data:",hgnc_infile)

  # Recent hgnc files have utf-8 (ie. non-ascii) characters for Alpha, Beta, etc, so open with utf-8 encoding:
  dataReader = csv.reader(open(hgnc_infile, encoding='utf-8'), dialect='excel-tab')
     # or: dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  row = next(dataReader)

  ihgnc = dict() # The column name to number for the above HGNC dict. 
  for i in range(len(row)): ihgnc[row[i]] = i   # Store column numbers for each item in the input header line.
  # Store these column numbers in globabl variables to access the array elements stored in the 'hgnc' dictionary:
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
  num_synonmys_already_exist = 0
  for row in dataReader:      
    if row[istatus] == 'Entry Withdrawn':
       continue  # So skip this entry.
       
    gene_name = row[isymbol] # The "ihgnc['symbol']" will be 1 - ie the second column, as 0 is the first column which is HGNC number
    cosmic_name = row[icosmic_id]
    if cosmic_name !='' and cosmic_name != gene_name:
      error("COSMIC '%s' != gene_name '%s'" %(cosmic_name,gene_name))
    if gene_name in hgnc:
      error("Duplicated gene_name '%s' status='%s' in HGNC file: Entrez: '%s' '%s' Ensembl '%s' '%s' \nrow: %s\nhgnc: %s" %(gene_name, row[istatus], hgnc[gene_name][ientrez_id], row[ientrez_id], hgnc[gene_name][iensembl_id], row[iensembl_id], row, hgnc[gene_name])  )
    hgnc[gene_name] = row # Store the whole row for simplicity.

    # Build dictionary of prev-names & synonyms to gene_names:
    # print("%s : prev_names=%s, synonyms=%s" %(gene_name,row[iprev_names],row[isynonyms]))    
    prevname_synonyms = row[iprev_names] + ('' if row[iprev_names]=='' or row[isynonyms]=='' else '|') + row[isynonyms]
    for key in prevname_synonyms.split('|'):
      if key == '': continue
      # print("  key:",key)
      if key in synonyms_to_hgnc:
        num_synonmys_already_exist += 1
        # print("**** ERROR: For gene %s Synonym %s already exists in gene %s:" %(gene_name,key,synonyms_to_hgnc[key]))
        synonyms_to_hgnc[key] += ';'+gene_name
        print("synonyms_to_hgnc[%s] = '%s'" %(key,synonyms_to_hgnc[key]))
      else:
        synonyms_to_hgnc[key] = gene_name
      # print (ihgnc['symbol'], hgnc[ihgnc['symbol']])

    # Build dictionary of entrez_id to gene_names:
    entrez_id = row[ientrez_id]
    if entrez_id in entrez_to_hgnc:
      entrez_to_hgnc[entrez_id] += ';'+gene_name
      print("entrez_to_hgnc[%s] = '%s'" %(entrez_id,entrez_to_hgnc[entrez_id]))
    else: 
      entrez_to_hgnc[entrez_id] = gene_name

  if num_synonmys_already_exist > 0: warn("%d prevnames/synonmys already exist in other genes" %(num_synonmys_already_exist))


      
# Dictionary used by function 'fix_gene_name(name)' to update some gene names, eg: 'C9orf96' to 'STKLD1', or changing '.' to '-'
namefixes = {
 'C9orf96':      'STKLD1', # as C9orf96 is the old name.
 'C8orf44.SGK3': 'C8orf44-SGK3',
 'CTB.89H12.4':  'CTB-89H12.4',
 'RP11.78H18.2': 'RP11-78H18.2',
 'NME1.NME2':    'NME1-NME2',
 'RP4.592A1.2':  'RP4-592A1.2',
 'FPGT.TNNI3K':  'FPGT-TNNI3K',
 'HLA.DQA1':     'HLA-DQA1',
 'HLA.DPA1':     'HLA-DPA1',
 'HLA.DRB1':     'HLA-DRB1',
 'HLA.DRB4':     'HLA-DRB4',
 'HLA.B':        'HLA-B',
 'HLA.C':        'HLA-C',
 'HLA.G':        'HLA-G',
 'HLA.H':        'HLA-H',
 'HLA.J':        'HLA-J',
 'ARL2.SNX15':   'ARL2-SNX15',
 'ERVFRD.1':     'ERVFRD-1',
 'TRIM6.TRIM34': 'TRIM6-TRIM34',
 'CYP1B1.AS1':   'CYP1B1-AS1',
 'SLX1B.SULT1A4':'SLX1B-SULT1A4',
 'LRRC75A.AS1':  'LRRC75A-AS1',
 'NDUFC2.KCTD14':'NDUFC2-KCTD14',
 'KRTAP10.5':    'KRTAP10.5',
 'SRP14.AS1':    'SRP14-AS1',
 'LOC100499484.C9ORF174': 'LOC100499484-C9ORF174'
}
      
def fix_gene_name(name):
  """ Updates some gene names, eg: 'C9orf96' to 'STKLD1', or changing first or second '.' to '-' and checking the hgnc dictionary for the updated name.  Currently the may length of gene_name column in models.py is 25 characters.
  """

  if len(name) > 25: fatal_error("gene_name '%s' >25 characters long" %(name))
  
  newname = ''
  
  if name in namefixes:
    newname = namefixes[name]  
    info("Changed: '%s' => '%s'" %(name,newname))
    return newname

  elif name.find('.') > -1:
     s = name.split('.')
     if len(s) == 1:
       fatal_error("fix_gene_name() split on '.' failed. This should never happen. name: %s" %(name))
     elif len(s) == 2:
       newname = "%s-%s" %(s[0],s[1])
       if newname in hgnc:
          info("Changed: '%s' => '%s'" %(name,newname))
          return newname
     elif len(s) == 3:
       newname = "%s-%s.%s" %(s[0],s[1],s[2])  # Try changing name "a.b.c" => "a-b.c"
       if newname in hgnc:
          info("Changed: '%s' => '%s'" %(name,newname))       
          return newname       
       newname = "%s.%s-%s" %(s[0],s[1],s[2])  # Try changing name "a.b.c" => "a.b-c"
       if newname in hgnc:
          info("Changed: '%s' => '%s'" %(name,newname))
          return newname
       newname = "%s-%s-%s" %(s[0],s[1],s[2])  # Try changing name "a.b.c" => "a-b-c"
       if newname in hgnc:
          return newname
     else:  # has >3  '.'
       fatal_error("fix_gene_name() has %d '.' in name: %s" %(len(s),name))

  return name


ATARmap = dict()
def load_mygene_hgnc_dictionary():
  """ Reads in the names from mygene data for the genes used in the R analysis of Achilles data """
  
  global ATARmap, jsol_entrez, img_entrezgene, img_symbol, img_hgnc, ihgnc_ensembl_id, img_ensembl_id, iname_used_for_R

  # The following file is produced by parse_Achilles_QC_v243_rna_Gs_gct.py:
  output_file4_newnames = os.path.join("Achilles_data", "Achilles_solname_to_entrez_map_with_names_used_for_R_v4_17Aug2016.txt")
  
  info("\nLoading ATARmap mygne dictionary from file: %s" %(output_file4_newnames))
  
  dataReader = csv.reader(open(output_file4_newnames), dialect='excel-tab')
  # Format for file:
  # sol.name        mg_symbol       entrez  mg_entrez  mg_hgnc  hgnc_ensembl     mg_ensembl       name_used_for_R
  # A2ML1_1_01110   A2ML1           144568  144568     23336    ENSG00000166535  ENSG00000166535  A2ML11_ENSG00000166535

  row = next(dataReader) # To read the first line which is the headings line of column names.

  cols = dict() # The column name-to-number for the above HGNC dictionary lists. 
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
      #if iname_used_for_R >= len(row): error("iname_used_for_R=%d > len(row)=%d" %(iname_used_for_R,len(row)), row)
      #key = row[iname_used_for_R]
      #if key in ATARmap:
      #  warn("Duplicate name_used_for_R %s in file: " %(key),row)
      #ATARmap[key] = row

      
      
      
RE_GENE_NAME = re.compile(r'^[0-9A-Za-z\-_\.]+$')

def find_or_add_gene(names, is_driver, is_target, isAchilles, isColt):
  """ Find or add a gene to the Gene table. 
      'names' - is a tuple or list of: [ gene_name, entrez_id, ensembl_id ]
     Trimming of the variant number from the Achilles target gene names is already done by the calling function. 
  """

  # Things to fix for Achilles data:
      # For gene 'DUX3': ensembl_id '' from HGNC doesn't match 'NoEnsemblIdFound' from R results file
      # Invalid number of parts in target gene, (as expected 2 parts) GTF2H2C_21_ENSG00000274675
      #     - is in the "Achilles_solname_to_entrez_map_with_names_used_for_R_v3_12Mar2016.txt" as:
      #       GTF2H2D_1_10001 GTF2H2C_2       730394  730394  35418           ENSG00000274675
      # WARNING: For gene 'GTF2H2': Ensembl_id 'ENSG00000145736' already saved in the Gene table doesn't match '21' from R results file
      # Invalid number of parts in target gene, (as expected 2 parts) but got: C4B_21_ENSG00000233312
      
  original_gene_name = names[0]
  names[0] = fix_gene_name(names[0])
  gene_name = names[0]
  entrez_id = names[1]
  if entrez_id == 'EntrezNotFound':
    info("Entrez id='%s' for gene %s, changing to 'NoEntrezId'" %(entrez_id,gene_name))    
    entrez_id='NoEntrezId' # As 'EntrezNotFound' from Achilles data is too long for the 10 character entrez_id field.
    names[1] = entrez_id
  ensembl_id = names[2]

# Remove this line later:         
  if original_gene_name=='BFP': print("1. BFP=>%s" %(gene_name))
  
  # Check that gene name_matches the current regexp in the gendep/urls.py file:
  assert RE_GENE_NAME.match(gene_name), "gene_name %s doesn't match regexp"%(gene_name)

  gene_found_in_entrez_info = False
  campbell_gene_found_in_entrez_info = False
  if isAchilles or isColt: # Then lookup gene info that was downloaded from NCBI Entrez:  
    if entrez_id not in entrez_info:
      warn("Achilles or Colt Entrez_id '%s' (gene_name '%s') NOT found in entrez_info dictionary" %(entrez_id,gene_name))
    else: 
      gene_found_in_entrez_info = True   
  else: # Campbell data  
    if gene_name not in entrez_info_gene_name_to_entrez:
      warn("Campbell gene: %s not found in entrez_info_gene_name_to_entrez" %(gene_name))
    else: campbell_gene_found_in_entrez_info = True  
    if ensembl_id not in entrez_info_ensembl_to_entrez:
      warn("Campbell ensembl %s (gene: %s) not found in entrez_info_ensembl_to_entrez" %(ensembl_id,gene_name))
    else: campbell_gene_found_in_entrez_info = True

# Remove this line later:         
  if original_gene_name=='BFP': print("2. BFP=>%s" %(gene_name))

    
  gene_found_in_hgnc = False
  if not gene_found_in_entrez_info:
    if gene_name in hgnc:
      gene_found_in_hgnc = True
    elif gene_name!='BFP' and gene_name in synonyms_to_hgnc: # Don't change BFP using synonyms:
      # print("Found gene_name %s in synonyms for %s" %(gene_name,synonyms_to_hgnc[gene_name]))
      new_name = synonyms_to_hgnc[gene_name]
      ## BUT This incorrectly means BFP => RNF112
      if ';' in new_name:
          print("** WARNING: '%s', '%s' BUT this prev-name / synonym is for two or more genes '%s'" %(original_gene_name,gene_name,new_name))
      else:
          warn("gene_name %s %s changed to %s using HGNC synonyms" %(original_gene_name,gene_name,new_name))      
          gene_name = new_name
          gene_found_in_hgnc = True
    else:
      warn("Gene '%s', '%s' (entrez='%s', ensembl='%s') NOT found in HGNC dictionary" %(original_gene_name,gene_name,entrez_id,ensembl_id) )

# Remove this line later:         
    if original_gene_name=='BFP': print("3. BFP=>%s" %(gene_name))

           
    if entrez_id != '' and entrez_id != 'NoEntrezId':
      if entrez_id in entrez_to_hgnc:
          # print("Found gene_name %s entrez_id %s in HGNC using Entrez_id for %s" %(gene_name,entrez_id,entrez_to_hgnc[entrez_id]))
          new_name = entrez_to_hgnc[entrez_id]
          if ';' in new_name:
              print("** WARNING: '%s', '%s' BUT this entrez_id %s is for two or more genes '%s'" %(original_gene_name,gene_name,entrez_id,new_name))
              # return gene_name+"_UnsureEntrez_"+new_name                
          if new_name == gene_name:
              gene_found_in_hgnc = True                
          else:            
              warn("***** ERROR: '%s', '%s' BUT this entrez_id %s is for two or more genes '%s'" %(original_gene_name,gene_name,entrez_id,new_name))
      else:        
         warn("Gene '%s', '%s' Entrez_id='%s' (ensembl='%s') NOT found in Entrez_to_HGNC dictionary" %(original_gene_name,gene_name,entrez_id,ensembl_id) )
         
# Remove this line later:         
  if original_gene_name=='BFP': print("4. BFP=>%s" %(gene_name))
  
  try:
    g = Gene.objects.get(gene_name=gene_name) # Gene already in Gene table
    # Update the is_driver and is_target status in the database (used for displaying the dropdrown search menu and displaying the drivers table):
    if is_driver and not g.is_driver:
      info("Updating '%s' to is_driver" %(gene_name))
      g.is_driver = is_driver
      g.save()
    if is_target and not g.is_target:
      info("Updating '%s' to is_target" %(gene_name))
      g.is_target = is_target
      g.save()
            
    # Test if stored entrez_id is same as already in database:
    g_entrez_id = g.entrez_id
    if entrez_id != '' and entrez_id != 'NoEntrezId' and g_entrez_id != entrez_id and not (entrez_id in entrez_secondary_ids and entrez_secondary_ids[entrez_id]==g_entrez_id):
      if g.entrez_id == '' or g_entrez_id == 'NoEntrezId':
        info("Updating entrez_id, as driver '%s' must have been inserted as a target first %s %s, is_driver=%s g.is_driver=%s, g.is_target=%s" %(g.gene_name,g.entrez_id,entrez_id,is_driver,g.is_driver, g.is_target))
        g.entrez_id=entrez_id
        g.save()
      else: 
        warn("For gene '%s': Entrez_id '%s' (%s, len=%d) already saved in the Gene table doesn't match '%s' (%s, len=%d) from the R results file" %(g.gene_name,g.entrez_id,type(g.entrez_id),len(g_entrez_id), entrez_id,type(entrez_id),len(entrez_id)))

    # Test if stored ensemble_id is same:
    if ensembl_id!='' and ensembl_id!='NoEnsemblIdFound' and g.ensembl_id != ensembl_id:
      if g.ensembl_id == '' or g.ensembl_id=='NoEnsemblIdFound':
        info("Updating Ensembl_id, as driver '%s' must have been inserted as a target first %s %s, is_driver=%s g.is_driver=%s, g.is_target=%s" %(g.gene_name,g.ensembl_id,ensembl_id,is_driver,g.is_driver, g.is_target))
        g.ensembl_id=ensembl_id
        g.save()
      else:
        warn("For gene '%s': Ensembl_id '%s' (%s, len=%d) already saved in the Gene table doesn't match '%s' (%s, len=%d) from R results file" %(g.gene_name, g.ensembl_id,type(g.ensembl_id),len(g.ensembl_id), ensembl_id,type(ensembl_id),len(ensembl_id)) )
          
  except ObjectDoesNotExist: # gene name not found in the gene table by the objects.get(), so need to add it:
    # if gene_name == 'PIK3CA': debug("PIK3CA Here B")
    
    alteration_considered = driver_alterations.get('_'.join(names), '')  # or should this be original_gene_name + ....
    if is_driver and alteration_considered=='': warn("alteration_considered is missing for driver '%s'" %('_'.join(names)))
    
    if not gene_found_in_entrez_info and not gene_found_in_hgnc:
      g = Gene.objects.create(gene_name=gene_name, original_name = original_gene_name, is_driver=is_driver, is_target=is_target, alteration_considered=alteration_considered, entrez_id=entrez_id, ensembl_id=ensembl_id)
      
    elif gene_found_in_entrez_info:
      this_entrez = entrez_info[entrez_id] # cache in a local variable to simplify code and reduce lookups.

      prevname_synonyms = this_entrez[ie_synonyms]
      full_name  = this_entrez[ie_desc]       # eg: erb-b2 receptor tyrosine kinase 2      
      entrez_id  = this_entrez[ie_entrez]       # eg: 2064
      ensembl_id = this_entrez[ie_ensembl_gene]      # eg: ENSG00000141736
      if ';' in ensembl_id: ensembl_id = ensembl_id[:ensembl_id.index(';')]   # As now a list of ensembl ids separated by semicolons so just take the first one in the list.
      # hprd_id    = this_entrez[ie_hprd]  # But HPRD seems not to be updated recently
      # maploc   = this_entrez[ie_maploc]
      cosmic_id  = this_entrez[ie_gene_name]       # eg: ERBB2
      omim_id    = this_entrez[ie_omim]         # eg: 164870
      if ';' in omim_id: omim_id = omim_id[:omim_id.index(';')]   # As now a list of omim ids separated by semicolons so just take the first one in the list.                        
      uniprot_id = this_entrez[ie_uniprot]      # eg: P04626
      if ';' in uniprot_id: uniprot_id = uniprot_id[:uniprot_id.index(';')]   # As now a list of uniprot ids separated by semicolons so just take the first one in the list.                  
      vega_id    = this_entrez[ie_vega]         # eg: OTTHUMG00000179300
      if ';' in vega_id: vega_id = vega_id[:vega_id.index(';')]   # As now a list of ensembl ids separated by semicolons so just take the first one in the list.      
      hgnc_id    = this_entrez[ie_hgnc].replace('HGNC:','')  # eg: HGNC:21998 (but remove the 'HGNC:' prefix)
      ensembl_protein = this_entrez[ie_ensembl_protein]
      if ';' in ensembl_protein: ensembl_protein = ensembl_protein[:ensembl_protein.index(';')] # As now a list of proteins separated by semicolons so just take the first one in the list and check this in the string-db alias file later.
      ncbi_summary = this_entrez[ie_summary]
      
      if gene_name != this_entrez[ie_gene_name]: info("gene_name '%s' != this_entrez '%s'" %(gene_name,this_entrez[ie_gene_name]))

*** fix the DUX4 entrez id to be just one number instead of 22947.100288687      
      #   = this_entrez[ie_status]
      #   = this_entrez[ie_current_entrez]
      #   = this_entrez[ie_current_locus]
      g = Gene.objects.create(
               gene_name = gene_name,         # hgnc[gene_name][ihgnc['symbol']]  eg. ERBB2
               original_name = original_gene_name,               
               is_driver  = is_driver,
               is_target  = is_target,
               alteration_considered = alteration_considered,
               full_name  = full_name,       # eg: erb-b2 receptor tyrosine kinase 2
               prevname_synonyms = prevname_synonyms,     # eg: NGL  (plus)  NEU|HER-2|CD340|HER2
               entrez_id  = entrez_id,       # eg: 2064
               ensembl_id = ensembl_id,      # eg: ENSG00000141736
               cosmic_id  = cosmic_id,       # eg: ERBB2
               omim_id    = omim_id,         # eg: 164870
               uniprot_id = uniprot_id,      # eg: P04626
               vega_id    = vega_id,         # eg: OTTHUMG00000179300
               hgnc_id    = hgnc_id,         # eg: 3430
               ensembl_protein_id = ensembl_protein,
               ncbi_summary = ncbi_summary
               # cancerrxgene_id = ....... ????

               # 'alias_name'       # eg: neuro/glioblastoma derived oncogene homolog|human epidermal growth factor receptor 2
               # 'gene_family'      # eg: CD molecules|Minor histocompatibility antigens|Erb-b2 receptor tyrosine kinases
               # 'refseq_accession' # eg: NM_004448
               )
    
    elif gene_found_in_hgnc:
    # Remove this line later:         
      if original_gene_name=='BFP': print("5. BFP=>%s" %(gene_name))

      this_hgnc = hgnc[gene_name] # cache in a local variable to simplify code and reduce lookups.
      if not campbell_gene_found_in_entrez_info: info("Adding Campbell gene: %s, %s, %s" %(original_gene_name,gene_name,this_hgnc))
      print("Adding:",original_gene_name,gene_name,this_hgnc)      
      if entrez_id != '' and entrez_id != this_hgnc[ientrez_id]:
        warn("For gene '%s': entrez_id '%s' from HGNC doesn't match '%s' from R results file" %(gene_name, this_hgnc[ientrez_id], entrez_id) )
        this_hgnc[ientrez_id] = entrez_id        # So change it to use the one from the Excel file.
      if ensembl_id != '' and ensembl_id != 'NoEnsemblIdFound' and ensembl_id != this_hgnc[iensembl_id]:
        warn("For gene '%s': ensembl_id '%s' from HGNC doesn't match '%s' from R results file" %(gene_name, this_hgnc[iensembl_id], ensembl_id) )
        this_hgnc[iensembl_id] = ensembl_id  # So change it to use the one from the Excel file.
      # The following uses the file downloaded from HGNC, but alternatively can use a web service such as: mygene.info/v2/query?q=ERBB2&fields=HPRD&species=human     or: http://mygene.info/new-release-mygene-info-python-client-updated-to-v2-3-0/ or python client:  https://pypi.python.org/pypi/mygene   http://docs.mygene.info/en/latest/doc/query_service.html  Fields available:  http://mygene.info/v2/gene/1017     http://docs.mygene.info/en/latest/
      # or uniprot: http://www.uniprot.org/help/programmatic_access  or Ensembl: http://rest.ensembl.org/documentation/info/xref_external
#      if info_source == 'HGNC':

      prevname_synonyms = this_hgnc[iprev_names] + ('' if this_hgnc[iprev_names] == '' or this_hgnc[isynonyms] == '' else ' | ') + this_hgnc[isynonyms].replace('|', ' | ') # Pad the synonyms with spaces as easier to read.
      
      # Added the above synonyms padding to the database manually for now using: update gendep_gene set prevname_synonyms = replace(prevname_synonyms, '|', ' | ');
      
      full_name  = this_hgnc[ifull_name]       # eg: erb-b2 receptor tyrosine kinase 2      
      entrez_id  = this_hgnc[ientrez_id]       # eg: 2064
      ensembl_id = this_hgnc[iensembl_id]      # eg: ENSG00000141736
      cosmic_id  = this_hgnc[icosmic_id]       # eg: ERBB2
      omim_id    = this_hgnc[iomim_id]         # eg: 164870
      uniprot_id = this_hgnc[iuniprot_id]      # eg: P04626
      vega_id    = this_hgnc[ivega_id]         # eg: OTTHUMG00000179300
      hgnc_id    = this_hgnc[ihgnc_id]


      # In HGNC some genes have two or three OMIM IDs, eg: gene "ATRX" has omim_id: "300032|300504" (length=13, but column width is 10, and simpler to just store first name)
      if len(omim_id) >= 9:
          pos = omim_id.find('|')
          if pos > -1:
            info("%s: using only first omid_id: %s" %(gene_name,omim_id))
            omim_id = omim_id[:pos]
      
      g = Gene.objects.create(
               gene_name = gene_name,         # hgnc[gene_name][ihgnc['symbol']]  eg. ERBB2
               original_name = original_gene_name,               
               is_driver  = is_driver,
               is_target  = is_target,
               alteration_considered = alteration_considered,
               full_name  = full_name,       # eg: erb-b2 receptor tyrosine kinase 2
               prevname_synonyms = prevname_synonyms,     # eg: NGL  (plus)  NEU|HER-2|CD340|HER2
               entrez_id  = entrez_id,       # eg: 2064
               ensembl_id = ensembl_id,      # eg: ENSG00000141736
               cosmic_id  = cosmic_id,       # eg: ERBB2
               omim_id    = omim_id,         # eg: 164870
               uniprot_id = uniprot_id,      # eg: P04626
               vega_id    = vega_id,         # eg: OTTHUMG00000179300
               hgnc_id    = hgnc_id
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
      else: error("Invalid Iinfo_source='%s'" %(info_source))
      """
    # debug( "*****", this_hgnc[iuniprot_id])
    # g.save() # Using create() above instead of Gene(...) and g.save.
    
  # if gene_name == 'PIK3CA': debug("PIK3CA Here C")
  return g


  

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
        error("count gene_name mismatch for '%s' and '%s'" %(g.gene_name,row['driver']))
      elif not g.is_driver: 
        error("count gene isn't marked as a driver '%s'" %(g.gene_name))
      else:
        g.driver_num_studies = row['num_studies']
        g.driver_num_histotypes = row['num_histotypes']
        g.driver_num_targets = row['num_targets']
        g.save()
    except ObjectDoesNotExist: # Not found by the objects.get()
      error("driver gene_name % NOT found in the Gene table: '%s'" %(row['driver']))
  print("Finished adding study, tissue and target counts to the drivers in the dependency table")

def add_counts_of_driver_tissue_and_target_to_studies(campbell_study, campbell_num_targets,  achilles_study, achilles_num_targets,  colt_study, colt_num_targets):
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
        error("count study mismatch for '%s' and '%s'" %(s.pmid,row['study']))
      else:
        if s == campbell_study:
           s.num_targets = campbell_num_targets
           print("But setting num_targets=%d (instead of %d) for Campbell study (pmid=%s) as that is actual number tested in the study" %(campbell_num_targets,row['num_targets'],campbell_study.pmid))
        elif s == achilles_study:
           s.num_targets = achilles_num_targets
           print("But setting num_targets=%d (instead of %d) for Achilles study (pmid=%s) as that is actual number tested in the study" %(achilles_num_targets,row['num_targets'],achilles_study.pmid))
        elif s == colt_study:
           s.num_targets = colt_num_targets
           print("But setting num_targets=%d (instead of %d) for Colt study (pmid=%s) as that is actual number tested in the study" %(colt_num_targets,row['num_targets'],colt_study.pmid))
        else:
           warn("Unknown pmid: %s" %(s.pmid))
           s.num_targets = row['num_targets']

        s.num_drivers = row['num_drivers']
        s.num_histotypes = row['num_histotypes']

        s.save()
    except ObjectDoesNotExist: # Not found by the objects.get()
      error("study pmid % NOT found in the Study table: '%s'" %(row['study']))
  print("Finished adding driver, tissue and target counts to the study table")


def read_achilles_R_results(result_file, study, tissue_type, isAchilles=True, isColt=True):

  if isAchilles and isColt: error("Cannot be both Achilles and Colt ******")

  #print("*** ONLY UPDATING BOXPLOT DATA ***")
  ONLY_UPDATE_BOXPLOT_DATA = False
  
  print("\nImporting table: ",result_file)

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
  if row[0] != 'marker': error("Expected header to start with 'marker', but found: %s" %(row))
  idriver = header_dict['marker']
  itarget = header_dict['target']
  iwilcox = header_dict['wilcox.p'] # should be 16 if zero based
  ieffect_size = header_dict['CLES'] # CLES = 'common language effect size'
  # Added: zA     zB    ZDiff
  iza = header_dict['zA']
  izb = header_dict['zB']
  izdiff = header_dict['ZDiff']
  itissue = header_dict.get('tissue', -1) # The 'pancan' file has no tissue column.
  iboxplotdata = header_dict['boxplot_data']
  
  dependency_rows_updated = 0
  dependency_rows_not_found_to_update=0
  
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

    names = split_target_gene_name(row[itarget], isAchilles=isAchilles, isColt=isColt)
    target_variant = ''
    if isAchilles:
        target_variant = names[0][-1:]  # As target variant is single integer after target gene name in my formatted Achilles target names.
        names[0] = names[0][:-1]
    
    target_gene = find_or_add_gene(names, is_driver=False, is_target=True, isAchilles=isAchilles, isColt=isColt)
        
    # If using Histotype table: histotype = find_or_add_histotype(row[3], full_name=None)  # was: if row[3] not in histotypes: histotypes.append(row[3])
    if tissue_type=='PANCAN': histotype = 'PANCAN' 
    elif tissue_type=='BYTISSUE' and itissue!=-1:
        histotype = row[itissue]   # As using CharField(choices=...) and now is validated in the model.
#        if histotype == "BONE": histotype = "OSTEOSARCOMA" # As in the Cambell(2016) R results this is called BONE, but converted to "OSTEOSARCOMA" in Tables S1K
        if histotype == "OSTEOSARCOMA": histotype = "BONE" # Achilles has some non-Osteoscarcoma bone tumore cell-lines (whereas Cambell(2016) is just Osteoscarcomas) 
    else: print("Invalid tissue_type='%s' or itissue=%d" %(tissue_type,itissue))
    
    mutation_type='Both'  # Default to 'Both' for current data now.

    # Using bulk_create() would be faster I think. See: http://vincent.is/speeding-up-django-postgres/  and https://www.caktusgroup.com/blog/2011/09/20/bulk-inserts-django/
    
    # Bulk create is actually slightly slower than adding record by record in SQLite, but in MySQL it will be faster

    key = driver_gene.gene_name + '_' + target_gene.gene_name + ' ' + histotype + '_' + study.pmid # Could maybe use the gene object id as key ?

    if ONLY_UPDATE_BOXPLOT_DATA:
      try:
        d = Dependency.objects.get(driver=driver_gene, target=target_gene, target_variant=target_variant, wilcox_p=row[iwilcox], effect_size=row[ieffect_size], za = row[iza], zb = row[izb], zdiff = row[izdiff], histotype=histotype, mutation_type=mutation_type, study=study)
        d.boxplot_data = row[iboxplotdata]
        d.save()
        dependency_rows_updated += 1
      except ObjectDoesNotExist: # Not found by the objects.get() - as is different Achilles target_variant
        dependency_rows_not_found_to_update += 1
        
      continue
        
    d = target_dict.get(key,None)
    if d is not None:
        if not isAchilles: error("The driver + target + histotype + study key '%s' should be unique for non-Achilles data" %(key))
        if row[iwilcox] < d.wilcox_p:
            if d.mutation_type != mutation_type:
                print("d.mutation_type(%s) != mutation_type(%s)" %(d.mutation_type, mutation_type))
            d.wilcox_p = row[iwilcox]
            d.effect_size = row[ieffect_size]
            # Added: zA     zB    ZDiff
            d.za = row[iza]
            d.zb = row[izb]
            d.zdiff = row[izdiff]
            d.boxplot_data = row[iboxplotdata]
            if d.target_variant == target_variant: print("** ERRROR: target_variant already in database for target_variant '%s' and key: '%s'" %(target_variant,key))
            d.target_variant = target_variant # Need to update the target_variant, as it is needed to retrieve the correct boxplot from the R boxplots, where image file is: driver_gene_target_gene+target_variant_histotype_Pmid.png
            count_replaced += 1
        else:
            count_not_replaced += 1        
    else:
        # Added: zA     zB    ZDiff
        
        d = Dependency(driver=driver_gene, target=target_gene, target_variant=target_variant, wilcox_p=row[iwilcox], effect_size=row[ieffect_size], za = row[iza], zb = row[izb], zdiff = row[izdiff], histotype=histotype, mutation_type=mutation_type, study=study, boxplot_data = row[iboxplotdata])
        # As inhibitors is a ManyToMany field so can't just assign it with: inhibitors=None, 
        # if not d.is_valid_histotype(histotype): error("Histotype %s NOT found in choices array %s" %(histotype, Dependency.HISTOTYPE_CHOICES))
        dependencies.append( d )
        target_dict[key] = d

    print("\r",count_added, end=" ")
    count_added += 1

  if ONLY_UPDATE_BOXPLOT_DATA:
    print("dependency_rows_updated:",dependency_rows_updated," dependency_rows_not_found_to_update:",dependency_rows_not_found_to_update)
    return

            
  print( "%d dependency rows were added to the database, %d replaced and %d not replaced, so %d target_variants" %(count_added,count_replaced, count_not_replaced, count_replaced+count_not_replaced))
  print( "%d dependency rows were skipped as wilcox_p > 0.05 or effect_size < 0.65" %(count_skipped))

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
    

def unmark_drivers_not_in_the_21genes(): # BUT this is no longer needed
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


def add_the_three_studies():
    # ============================================================================================
    Campbell_study_pmid = "26947069"
    study_code = "B" # 'B' for campBell
    study_short_name = "Campbell(2016)"
    study_title = "Large Scale Profiling of Kinase Dependencies in Cancer Cell Line"
    study_authors = "Campbell J, Ryan CJ, Brough R, Bajrami I, Pemberton H, Chong I, Costa-Cabral S, Frankum J, Gulati A, Holme H, Miller R, Postel-Vinay S, Rafiq R, Wei W, Williamson CT, Quigley DA, Tym J, Al-Lazikani B, Fenton T, Natrajan R, Strauss S, Ashworth A, Lord CJ"
    study_abstract = "One approach to identifying cancer-specific vulnerabilities and novel therapeutic targets is to profile genetic dependencies in cancer cell lines. Here we use siRNA screening to estimate the genetic dependencies on 714 kinase and kinase-related genes in 117 different tumor cell lines. We provide this dataset as a resource and show that by integrating siRNA data with molecular profiling data, such as exome sequencing, candidate genetic dependencies associated with the mutation of specific cancer driver genescan be identified. By integrating the identified dependencies with interaction datasets, we demonstrate that the kinase dependencies associated with many cancer driver genes form dense connections on functional interaction networks. Finally, we show how this resource may be used to make predictions about the drug sensitivity of genetically or histologically defined subsets of cell lines, including an increased sensitivity of osteosarcoma cell lines to FGFR inhibitors and SMAD4 mutant tumor cells to mitotic inhibitors."
    study_summary = "siRNA screen of 714 kinase and kinase-related genes in 117 different tumor cell lines"
    study_experiment_type = "kinome siRNA"
    study_journal = "Cell reports"
    study_pub_date = "2016, 2 Mar"
    Campbell_study_num_targets = 713  # check this

    Campbell_study=find_or_add_study( Campbell_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date)

    # ============================================================================================
    # Project Achilles: # https://www.broadinstitute.org/achilles  and http://www.nature.com/articles/sdata201435
    Achilles_study_pmid     = "25984343"
    study_code = "A" # 'A' for Achilles
    study_short_name = "Cowley(2014)"
    study_title = "Parallel genome-scale loss of function screens in 216 cancer cell lines for the identification of context-specific genetic dependencies."
    study_authors = "Cowley GS, Weir BA, Vazquez F, Tamayo P, Scott JA, Rusin S, East-Seletsky A, Ali LD, Gerath WF, Pantel SE, Lizotte PH, Jiang G, Hsiao J, Tsherniak A, Dwinell E, Aoyama S, Okamoto M, Harrington W, Gelfand E, Green TM, Tomko MJ, Gopal S, Wong TC, Li H, Howell S, Stransky N, Liefeld T, Jang D, Bistline J, Hill Meyers B, Armstrong SA, Anderson KC, Stegmaier K, Reich M, Pellman D, Boehm JS, Mesirov JP, Golub TR, Root DE, Hahn WC"
    study_abstract = "Using a genome-scale, lentivirally delivered shRNA library, we performed massively parallel pooled shRNA screens in 216 cancer cell lines to identify genes that are required for cell proliferation and/or viability. Cell line dependencies on 11,000 genes were interrogated by 5 shRNAs per gene. The proliferation effect of each shRNA in each cell line was assessed by transducing a population of 11M cells with one shRNA-virus per cell and determining the relative enrichment or depletion of each of the 54,000 shRNAs after 16 population doublings using Next Generation Sequencing. All the cell lines were screened using standardized conditions to best assess differential genetic dependencies across cell lines. When combined with genomic characterization of these cell lines, this dataset facilitates the linkage of genetic dependencies with specific cellular contexts (e.g., gene mutations or cell lineage). To enable such comparisons, we developed and provided a bioinformatics tool to identify linear and nonlinear correlations between these features."
    study_summary = "shRNA screen of 11,000 genes in 216 different cancer cell lines, with 5 shRNAs per gene"
    study_experiment_type = "genome shRNA"
    study_journal = "Scientific Data"
    study_pub_date = "2014, 30 Sep"
    Achilles_study_num_targets = 5013 # see my email
    
    Achilles_study=find_or_add_study( Achilles_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date )

    # ==================================================================================================
    # Colt:  https://neellab.github.io/bfg/   https://www.ncbi.nlm.nih.gov/pubmed/26771497
   
    Colt_study_pmid = "26771497"
    study_code = "C"  # 'C' for Colt
    study_short_name = "Marcotte(2016)"
    study_title = "Functional Genomic Landscape of Human Breast Cancer Drivers, Vulnerabilities, and Resistance."
    study_authors = "Marcotte R, Sayad A, Brown KR, Sanchez-Garcia F, Reimand J, Haider M, Virtanen C, Bradner JE, Bader GD, Mills GB, Pe'er D, Moffat J, Neel BG"
    study_abstract = "Large-scale genomic studies have identified multiple somatic aberrations in breast cancer, including copy number alterations and point mutations. Still, identifying causal variants and emergent vulnerabilities that arise as a consequence of genetic alterations remain major challenges. We performed whole-genome small hairpin RNA (shRNA) \"dropout screens\" on 77 breast cancer cell lines. Using a hierarchical linear regression algorithm to score our screen results and integrate them with accompanying detailed genetic and proteomic information, we identify vulnerabilities in breast cancer, including candidate \"drivers,\" and reveal general functional genomic properties of cancer cells. Comparisons of gene essentiality with drug sensitivity data suggest potential resistance mechanisms, effects of existing anti-cancer drugs, and opportunities for combination therapy. Finally, we demonstrate the utility of this large dataset by identifying BRD4 as a potential target in luminal breast cancer and PIK3CA mutations as a resistance determinant for BET-inhibitors."
    study_summary = "shRNA screen of on 77 breast cancer cell lines. Dropout trends for each screen in at three time points (8-9 arrays per screen, and a total of 621 arrays)"
    study_experiment_type = "genome shRNA"
    study_journal = "Cell"
    study_pub_date = "2016, 14 Jan"
    Colt_study_num_targets = 15697 # The actual number of targets tested in the Colt (Marcotte et al) study, although only 8,898 dependencies are in the dependency table, as rest don't meet the (p<=0.05 and effect_size>=0.65) requirement.

    Colt_study=find_or_add_study( Colt_study_pmid, study_code, study_short_name, study_title, study_authors, study_abstract, study_summary, study_experiment_type, study_journal, study_pub_date )
    
    return Campbell_study,Achilles_study,Colt_study,  Campbell_study_num_targets,  Achilles_study_num_targets, Colt_study_num_targets
    

if __name__ == "__main__":
# add_tissue_and_study_lists_for_each_driver()

  ##unmark_drivers_not_in_the_21genes()
  
  #add_counts_of_driver_tissue_and_target_to_studies()

  load_entrez_gene_full_details_for_Achilles_and_Colt(entrez_gene_full_details_for_Achilles_and_Colt_infile)
  load_driver_alterations_dictionary()
  
  # sys.exit()
  #exit()
    

  load_hgnc_dictionary(hgnc_infile)
  load_mygene_hgnc_dictionary()
  
  
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each save()
    # Before using atomic(), I tried "transaction.set_autocommit(False)" but got error "Your database backend doesn't behave properly when autocommit is off."
    
    print("\nEmptying database tables")
    for table in (Dependency, Study, Gene): table.objects.all().delete()  # removed: Histotype, Drug
    # print("*** NOT deleting Dependency rows for now, as no change in Studies or Genes ****")
    

    Campbell_study, Achilles_study, Colt_study, Campbell_study_num_targets, Achilles_study_num_targets, Colt_study_num_targets = add_the_three_studies()
    
    analysis_dir = "198_boxplots_for_Colm/analyses"
    
    # analysis_dir = "postprocessing_R_results" # After Aug 2016

    # *** NOTE, warnings from R:
    # There were 50 or more warnings (use warnings() to see the first 50)

    # 44: In wilcox.test.default(zscores[grpA, j], zscores[grpB,  ... :
    # cannot compute exact p-value with ties
    
    Achilles_results_pancan =  "univariate_results_Achilles_v4_for36drivers_pancan_kinome_combmuts_26Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"
    # "univariate_results_Achilles_v2_for23drivers_pancan_kinome_combmuts_5May2016_witheffectsize_and_zdiff_and_boxplotdata.txt"
    csv_filepathname=os.path.join(analysis_dir, Achilles_results_pancan)
    read_achilles_R_results(csv_filepathname, Achilles_study, tissue_type='PANCAN', isAchilles=True, isColt=False)    
    
    #Achilles_results_bytissue = "univariate_results_Achilles_v2_for21drivers_bytissue_kinome_combmuts_160312_preeffectsize.txt"
    Achilles_results_bytissue = "univariate_results_Achilles_v4_for36drivers_bytissue_kinome_combmuts_26Aug2016witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"

    csv_filepathname=os.path.join(analysis_dir, Achilles_results_bytissue)
    read_achilles_R_results(csv_filepathname, Achilles_study, tissue_type='BYTISSUE', isAchilles=True, isColt=False)


    # ========================================================
    # Reading the Campbell results last as Achilles and Colt may have already loaded the Entrez gene annotations above.    
    Campbell_results_pancan= "univariate_results_Campbell_v26_for36drivers_pancan_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"

    # "univariate_results_v26_pancan_kinome_combmuts_28April2016_witheffectsize_and_zdiff_and_boxplotdata.txt"    
    csv_filepathname=os.path.join(analysis_dir, Campbell_results_pancan)
    read_achilles_R_results(csv_filepathname, Campbell_study, tissue_type='PANCAN', isAchilles=False, isColt=False)

    Campbell_results_bytissue = "univariate_results_Campbell_v26_for36drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"
    
    # "univariate_results_v26_bytissue_kinome_combmuts_28April2016_witheffectsize_and_zdiff_and_boxplotdata.txt"
    csv_filepathname=os.path.join(analysis_dir, Campbell_results_bytissue)
    read_achilles_R_results(csv_filepathname, Campbell_study, tissue_type='BYTISSUE', isAchilles=False, isColt=False)

    # ========================================================

    
    #** Maybe my browser memory?
    #https://www.ncbi.nlm.nih.gov/pubmed/
    #Bad Request

    #Your browser sent a request that this server could not understand.
    #Size of a request header field exceeds server limit.
    #Cookie
    #/n

    # Colt_results_pancan = "NONE" - as Colt is only Breast tissue
    Colt_results_bytissue = "univariate_results_Colt_v2_for36drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"
        
    # "univariate_results_Colt_v1_bytissue_kinome_combmuts_7May2016_witheffectsize_and_zdiff_and_boxplotdata.txt"
    csv_filepathname=os.path.join(analysis_dir, Colt_results_bytissue)
    read_achilles_R_results(csv_filepathname, Colt_study, tissue_type='BYTISSUE', isAchilles=False, isColt=True)
    
    # I downloaded: https://neellab.github.io/bfg/
    # "updated shRNA annotations: Update to Entrez gene ids and symbols, to account for changed symbols, deprecated Entrez ids and the like. Approximately 300 gene ids from the original TRC II annotations no longer exist, leading to a slightly reduced overall gene id and shRNA count."
    
    # ============================================================================================
    add_counts_of_study_tissue_and_target_to_drivers()
    #### ***** and add counts of num_drivers 
    add_counts_of_driver_tissue_and_target_to_studies(    
        campbell_study=Campbell_study, campbell_num_targets=Campbell_study_num_targets,
        achilles_study=Achilles_study, achilles_num_targets=Achilles_study_num_targets,
        colt_study=Colt_study,         colt_num_targets=Colt_study_num_targets
    )
    
    add_tissue_and_study_lists_for_each_driver()
