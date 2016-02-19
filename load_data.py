# Script to import the data into the database tables
# An alternative if loading data into empty database is using 'Fixtures': https://docs.djangoproject.com/en/1.9/howto/initial-data/
# or django-adapters: http://stackoverflow.com/questions/14504585/good-ways-to-import-data-into-django
#                     http://django-adaptors.readthedocs.org/en/latest/

import os, csv

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


from gendep.models import Study, Gene, Dependency

def add_study(pmid, title, authors, description, summary, journal, pub_date):
  # Add one dummy study:
  if Study.objects.filter(pmid=pmid).exists():
    s = Study.objects.get(pmid=pmid)
  else:
    s=Study(pmid=pmid, title=title, authors=authors, description=description, summary=summary, journal=journal, pub_date=pub_date) # pub_date=...
    s.save()
  return s


# Maybe need a table of Histotypes ?


def split_driver_gene_name(long_name):
  # Driver format is: CCND1_595_ENSG00000110092
  names = long_name.split('_')
  if len(names)!=3:
    print('Invalid number of parts in driver gene, (as expected 3 parts)',long_name)
  #print(long_name,names)
  return names


def split_target_gene_name(long_name):
  # Target format is: DCK_ENSG00000156136
  # But an exception is: CDK12_ENSG00000167258_CRK7 (CRK7 is an alternative name)
  names = long_name.split('_')
  if len(names)!=2:
    if names[0] == 'CDK12' and len(names)==3: # as CDK12_ENSG00000167258_CRK7 (CRK7 is an alternative name)
      print('Removed last name from list', long_name, names.pop()) # Just remove last name from the list
    else:    
      print('Invalid number of parts in target gene, (as expected 2 parts)',long_name)
  names.insert(1,'') # or None, but Django stores None as empty string, rather than as null
  #print(long_name,names)
  return names



hgnc = dict() # To read the ids into a dictionary
# isymbol=-1; ifullname=-1; isynonyms=-1; iprevsymbol=-1; iensembl=-1; ientrez=-1; icosmic=-1; iomim=-1; iuniprot=-1; ihgnc=-1;   ialiasname=-1; ifamily=-1; ivega=-1; irefseq=-1;  

def load_hgnc_dictionary():
  global isymbol, ifullname,  isynonyms, iprevsymbol, iensembl, ientrez, icosmic, iomim, iuniprot, ihgnc, ialiasname, ifamily, ivega, irefseq
  infile = os.path.join('input_data','hgnc_complete_set.txt')
  dataReader = csv.reader(open(infile), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')
  is_header = True

  for row in dataReader:
    if is_header:
      #head = row
      for i in range(len(row)):
        if   row[i] == 'hgnc_id':          ihgnc = i       # eg: 3430
        elif row[i] == 'symbol':           isymbol = i     # eg. ERBB2
        elif row[i] == 'name':             ifullname = i   # eg: erb-b2 receptor tyrosine kinase 2
        elif row[i] == 'alias_symbol':     isynonyms = i   # eg: NEU|HER-2|CD340|HER2
        elif row[i] == 'alias_name':       ialiasname = i  # eg: neuro/glioblastoma derived oncogene homolog|human epidermal growth factor receptor 2
        elif row[i] == 'prev_symbol':      iprevsymbol = i # eg: NGL
        elif row[i] == 'gene_family':      ifamily = i     # eg: CD molecules|Minor histocompatibility antigens|Erb-b2 receptor tyrosine kinases
        elif row[i] == 'entrez_id':        ientrez = i     # eg: 2064
        elif row[i] == 'ensembl_gene_id':  iensembl = i    # eg: ENSG00000141736
        elif row[i] == 'vega_id':          ivega = i       # eg: OTTHUMG00000179300
        elif row[i] == 'refseq_accession': irefseq = i     # eg: NM_004448
        elif row[i] == 'uniprot_ids':      iuniprot = i    # eg: P04626
        elif row[i] == 'cosmic':           icosmic = i     # eg: ERBB2
        elif row[i] == 'omim_id':          iomim = i       # eg: 164870
      is_header = False

    # elif row[isymbol] in ('ERBB2', 'VEGFA', 'CFH'):
    # print (row[isymbol], row[ifullname], row[isynonyms], row[iprevsymbol], row[iensembl], row[ientrez], row[icosmic], row[iomim], row[iuniprot], row[ihgnc])
    else:
      hgnc[row[isymbol]] = row # Just store whole row for simplicity.  (row[isymbol], row[iname], row[isynonyms], row[iprevsymbol], row[iensembl], row[ientrez], row[icosmic], row[iomim], row[iuniprot], row[ihgnc])
      

def find_or_add_gene(names, is_driver):  # names is a tuple of: gene_name, entrez_id, ensembl_id
  name = names[0]
  
  #if name == 'CDK12':
  #    print(names)
  #    print("Gene info:",name, hgnc[name][ifullname], hgnc[name][isynonyms], hgnc[name][iprevsymbol], "entrez=", hgnc[name][ientrez], "ensembl=",hgnc[name][iensembl], hgnc[name][icosmic], hgnc[name][iomim], hgnc[name][iuniprot], hgnc[name][ihgnc] ) # cancerrxgene_id        

  if Gene.objects.filter(gene_name=name).exists():  # Alternatively use .object.get(...) and catch the exception if doesn't exist.
    # Test if ensemble_id is same:
    g = Gene.objects.get(gene_name=name)
    if names[1] != '' and g.entrez_id != names[1]:
      if g.entrez_id != '':
        print('Warning: For gene "%s" the Entrez_id "%s" already saved in the Gene table does NOT match the "%s" from the Excel file' %(g.gene_name,g.entrez_id,names[1]))
      else:
        print('*** Updating entrez_id, as driver must have been inserted as a target first:',g.gene_name,g.entrez_id,names[1])
        g.entrez_id=names[1]
        g.is_driver=is_driver
        g.save()
    if g.ensembl_id != names[2]: print('Warning: For gene "%s" the Ensembl_id "%s" already saved in the Gene table does NOT match the "%s" from the Excel file' %(g.gene_name,g.ensembl_id,names[2]) )

  else:
    # print ('Gene adding: ',names)
    if name not in hgnc:
      print("Gene NOT found in HGNC dictionary", name)
      g = Gene(gene_name=name, is_driver=is_driver, entrez_id=names[1], ensembl_id=names[2])
    else:  
      if names[1] != '' and names[1] != hgnc[name][ientrez]:
        print('*** For gene "%s" the entrez_id "%s" from HGNC does NOT match the "%s" from the Excel file' %(name, hgnc[name][ientrez], names[1]) )
      if names[2] != hgnc[name][iensembl]:
        print('***For gene "%s" the ensembl_id "%s" from HGNC does NOT match the "%s" from the Excel file' %(name, hgnc[name][iensembl], names[2]) )
#      print("Gene adding:",name, hgnc[name][ifullname], hgnc[name][isynonyms], hgnc[name][iprevsymbol], hgnc[name][ientrez], hgnc[name][iensembl], hgnc[name][icosmic], hgnc[name][iomim], hgnc[name][iuniprot], hgnc[name][ihgnc] ) # cancerrxgene_id        
      g = Gene(gene_name=name,
             is_driver=is_driver,
             full_name = hgnc[name][ifullname],
             synonyms = hgnc[name][isynonyms],
             prev_names = hgnc[name][iprevsymbol],
             entrez_id = hgnc[name][ientrez],  # entrez_id=names[1]
             ensembl_id = hgnc[name][iensembl], # ensembl_id=names[2]
             cosmic_id = hgnc[name][icosmic],
             # cancerrxgene_id = ....... ????
             )    
    g.save()
  return g



def import_data_from_tsv_table(csv_filepathname, table_name, study):
  print("Importing table: ",csv_filepathname)
  dataReader = csv.reader(open(csv_filepathname), dialect='excel-tab')  # dataReader = csv.reader(open(csv_filepathname), delimiter=',', quotechar='"')

  histotypes = list() # To store the unique histotype - better to use a database table in future

  for row in dataReader:
    if row[0] == 'Driver': continue  # Ignore the header row, import everything else
    driver_gene=split_driver_gene_name(row[0])
    driver_gene_object=find_or_add_gene(driver_gene, True)

    target_gene=split_target_gene_name(row[1])
    target_gene_object=find_or_add_gene(target_gene, False)

    # print('Dependency adding: ',driver_gene[0], target_gene[0], row[2], row[3])
#    if Dependency.objects.filter(driver=driver_gene[0], target=target_gene[0]).exists(): print('Driver-Target already exists in Dependency table ',driver_gene[0],target_gene[0])
#    d = Dependency(driver=driver_gene[0], target=target_gene[0], wilcox_p=row[2], histotype=row[3], study_pmid=study)  # study_pmid=''

    # When loading the second table 'S1K', it contains duplicates of the Driver-Target pairs that were in 'S1I', which is ok.
    # if Dependency.objects.filter(driver=driver_gene_object, target=target_gene_object, histotype=row[3]).exists(): print('Driver-Target-Histotype already exists in Dependency ',driver_gene[0],target_gene[0],row[3])
    mutation_type='Both'  # Default to 'Both' for current data now.
    
    if row[3] not in histotypes: histotypes.append(row[3])
    
    d = Dependency(study_table=table_name, driver=driver_gene_object, target=target_gene_object, wilcox_p=row[2], histotype=row[3], mutation_type=mutation_type, study_pmid=study)  # study_pmid=''

    d.save()
    
  print(histotypes)



if __name__ == "__main__":

  # print(os.getcwd())

  load_hgnc_dictionary()
  # print (hgnc['ERBB2'])
  # print( isymbol, ifullname,  isynonyms, iprevsymbol, iensembl, ientrez, icosmic, iomim, iuniprot, ihgnc, ialiasname, ifamily, ivega, irefseq )
  
  study_pmid = "Pending_0001"
  study_title = "Large Scale Profiling of Kinase Dependencies in Cancer Cell Line"
  study_authors = "James Campbell, Colm J. Ryan, Rachel Brough, Ilirjana Bajrami, Helen Pemberton, Irene Chong, Sara Costa-Cabral,Jessica Frankum, Aditi Gulati, Harriet Holme, Rowan Miller, Sophie Postel-Vinay, Rumana Rafiq, Wenbin Wei,Chris T Williamson, David A Quigley, Joe Tym, Bissan Al-Lazikani, Timothy Fenton, Rachael Natrajan, Sandra Strauss, Alan Ashworth and Christopher J Lord"
  study_description = "Summary: One approach to identifying cancer-specific vulnerabilities and novel therapeutic targets is to profile genetic dependencies in cancer cell lines. Here we use siRNA screening to estimate the genetic dependencies on 714 kinase and kinase-related genes in 117 different tumor cell lines. We provide this dataset as a resource and show that by integrating siRNA data with molecular profiling data, such as exome sequencing, candidate genetic dependencies associated with the mutation of specific cancer driver genescan be identified. By integrating the identified dependencies with interaction datasets, we demonstrate that the kinase dependencies associated with many cancer driver genes form dense connections on functional interaction networks. Finally, we show how this resource may be used to make predictions about the drug sensitivity of genetically or histologically defined subsets of cell lines, including an increased sensitivity of osteosarcoma cell lines to FGFR inhibitors and SMAD4 mutant tumor cells to mitotic inhibitors."
  study_summary = "siRNA screen of 714 kinase and kinase-related genes in 117 different tumor cell lines"
  study_journal = "Cell reports"
  study_pub_date = "2016"

  study=add_study( study_pmid, study_title, study_authors, study_description, study_summary, study_journal, study_pub_date)
  
  for table_name in ('S1I', 'S1K'):
    csv_filepathname=os.path.join(PROJECT_DIR, os.path.join('input_data', 'Table_'+table_name+'_min_cols.txt'))   # Full path and name to the csv file
    import_data_from_tsv_table(csv_filepathname,table_name,study)
