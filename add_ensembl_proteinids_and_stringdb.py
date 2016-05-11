#!/usr/bin/env python

import sys, os, sqlite3
from django.db import transaction
import mygene

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")
import django
django.setup()

# The following import needs to be after django.setup()
from gendep.models import Gene, Dependency  # Study, Drug.  Removed: Histotype


# Got contact at StringDB from Help page email: Peer Bork: bork@embl.de
#  http://string-db.org/newstring_cgi/show_download_page.pl

  
  

entrez_to_stringdb_protein_ids_input_file = "StringDB/entrez_gene_id.vs.string.v10.28042015.tsv"
# Got these entrez mappings from: http://string-db.org/mapping_files/entrez_mappings/
# ie: http://string-db.org/mapping_files/entrez_mappings/entrez_gene_id.vs.string.v10.28042015.tsv
# Format is:
#  #Entrez_Gene_ID STRING_Locus_ID
#  1       9606.ENSP00000263100
#  2       9606.ENSP00000323929
#  etc...

protein_alias_file = "StringDB/9606.protein.aliases.v10.txt"
# Got from bottom of page: http://string-db.org/newstring_cgi/show_download_page.pl
# Format:
#   ## string_protein_id ## alias ## source ##
#   9606.ENSP00000360761     1-@ACYLGLYCEROL-3-PHOSPHATE O-ACYL [*603100]   Ensembl_MIM_GENE
#   9606.ENSP00000380184     1-@ACYLGLYCEROL-3-PHOSPHATE O-ACYL [*608143]   Ensembl_MIM_GENE
# But also:
# 9606.ENSP00000320485    ARID1A  BLAST_KEGG_NAME BLAST_UniProt_DE BLAST_UniProt_GN BioMart_HUGO Ensembl_EntrezGene Ensembl_HGNC Ensembl_UniProt Ensembl_UniProt_DE Ensembl_UniProt_GN Ensembl_WikiGene
#9606.ENSP00000320485    ARID1A protein  BLAST_UniProt_DE Ensembl_UniProt_DE
#9606.ENSP00000320485    ARID1A variant protein  BLAST_UniProt_DE BLAST_UniProt_GN
#9606.ENSP00000320485    ARID1A-001      Ensembl_HGNC_transcript_name Ensembl_Vega_transcript
#9606.ENSP00000320485    ARID1A-002      Ensembl_HGNC_transcript_name Ensembl_Vega_transcript
"""
# From StringDB FAQ page: http://string-db.org/help/topic/org.string-db.docs/ch04.html
This file has four columns: species_ncbi_taxon_id, protein_id, alias, source. To figure out which is the string identifier for trpA in E. coli K12, you can do something like this in you terminal:

 
          zgrep ^83333 protein.aliases.v8.3.txt.gz | grep trpB
          
which would return:

 
          83333	b1261	trpB	BLAST_UniProt_GN RefSeq
          
from this you can get the string name by concatenating the two first column with a period (83333.b1261)

Q:	
Is there an automatic way of to mapping proteins to STRING? I need mappings for more three thousand proteins.

A:

A convenient way of mapping your proteins to STRING entries is to use the STRING API. As an example, for a single protein, the alias can be retrieved by:

 http://string-db.org/api/tsv/resolve?identifier=trpA\&amp;species=83333
Alternatively, instead of making on call per protein you can try to all the identifiers for a list of protein (separated by '%0D'):

 http://string-db.org/api/tsv/resolveList?identifiers=trpA%0DtrpB\&amp;species=83333
In such cases you may have a problems with the length limit of the URL, but this can be circumvented by sending the request as a HTTP POST request. For example using cURL:

 
          curl -d "identifiers=trpA%0DtrpC%0DtrpB%0DtrpD\&amp;species=83333" string-db.org/api/tsv/resolveList
"""

protein_interaction_input_file = "StringDB/stringdb_homo_sapiens_9606.protein.links.v10.txt"
# Got from http://string-db.org/newstring_cgi/show_download_page.pl
#   with filter menu set to 'Humo sapiens'

# Format is one space between columns:
# protein1 protein2 combined_score
# 9606.ENSP00000000233 9606.ENSP00000003084 150
# 9606.ENSP00000000233 9606.ENSP00000003100 215
# 9606.ENSP00000000233 9606.ENSP00000005257 223
# etc....
# all proteins seem to be prefixed with "9606" -is that for Human
# "Protein identifiers in the above files contain two substrings each: 'NNNNN.aaaaaa'. The first substring is the NCBI taxonomy species identifier, and the second substring is the RefSeq/Ensembl-identifier of the protein."



"""
# From: http://string-db.org/help/index.jsp?topic=/org.string-db.docs/ch04.html
You can use the file of protein aliases available from the download page protein.aliases.v8.3.txt.gz. This file has four columns: species_ncbi_taxon_id, protein_id, alias, source. To figure out which is the string identifier for trpA in E. coli K12, you can do something like this in you terminal:

 
          zgrep ^83333 protein.aliases.v8.3.txt.gz | grep trpB
          
which would return:

 
          83333	b1261	trpB	BLAST_UniProt_GN RefSeq
          
from this you can get the string name by concatenating the two first column with a period (83333.b1261)

# curl "http://string-db.org/api/tsv/resolve?identifier=ERBB2&species=9606" > string_id.junk

9606.ENSP00000354910    9606    Homo sapiens    NRG2    neuregulin 2; Direct ligand for ERBB3 and ERBB4 ....
9606.ENSP00000331305    9606    Homo sapiens    TOB2    .....
...
9606.ENSP00000269571    9606    Homo sapiens    ERBB2   v-erb-b2 erythroblastic leukemia viral ....
....
"""

def extract_ensembl_ids(id, result):
    ensembl_gene = None
    ensembl_proteins = None

    # successful result either:
    # {'ensembl.gene': 'ENSG00000149313', '_id': '60496', 'symbol': 'AASDHPPT'}
    # {'ensembl': [{'gene': 'ENSG00000275700'}, {'gene': 'ENSG00000276072'}], '_id': '26574', 'symbol': 'AATF'}
    
    if 'ensembl' in result:
        ensembl = result['ensembl']
        if 'protein' in ensembl:
            ensembl_proteins = ensembl['protein']
            print("ensembl protein:", ensembl_proteins)
        if 'gene' in ensembl:
            ensembl_gene = ensembl['gene']
            print("ensembl gene:", ensembl_gene)
            
    if 'ensembl.gene' in result:
        ensembl_gene = result['ensembl.gene']
        print("ensembl.gene:", ensembl_gene)
    if 'ensembl.protein' in result:
        ensembl_proteins = result['ensembl.protein']
        print("ensembl.protein:", ensembl_proteins)

    # Processing array of hits:
    if 'gene' in result:
        ensembl_gene = result['gene']
        print("gene:", ensembl_gene)        
    if 'protein' in result:
        ensembl_proteins = result['protein']
        print("protein:", ensembl_proteins)

        
    return ensembl_gene, ensembl_proteins        


def join_as_lists(a,b):
    if a is None:
        if isinstance(b,list): return b
        else: return [b,]
    elif isinstance(a,str): a=[a,]
    elif not isinstance(a,list): print("Unexpected type for a")

    if b is None: return a
    elif isinstance(b,str): a.append(b) # Needed to use append otherwise splits string b into list of individual characters.
    elif isinstance(b,list): a.extend(b)
    else: print("Unexpected type for b")
    
    return a

# Test:
#print(join_as_lists([1,2],[3,4]))
#print(join_as_lists('A',[3,4]))
#print(join_as_lists([3,4],'B'))
#print(join_as_lists('A','B'))
#print(join_as_lists('A',None))
#print(join_as_lists(None,'B'))

mg = mygene.MyGeneInfo()
#fields = mg.get_fields()
#for k in fields: print("\n",k,fields[k])

def lookup_entrez_id(id):
    print("  Looking in MyGene for entrez_id:", id)
    result = mg.getgene(id, fields="ensembl.protein, symbol, ensembl.gene, entrezgene, HGNC", email="sbridgett@gmail.com")

    if result is None:
        print("  No matches found in MyGene for entrez_id: '%s'" %(id))
        return None,None
#        return ensembl_gene, ensembl_proteins

        # entrez_ids = ["1017","7248"]
    if str(result['_id']) != id:
        print("*** Warning: returned id %s doesn't match query %s" %(result['_id'],id))

    if 'entrezgene' in result:
        if str(result['entrezgene']) != id:
            print("entrezgene:", result['entrezgene'], "doesn't match request:",id)
            
        # entrez_ids = ["1017","7248"]
    #else:
#        if result['_id'] != id:
#            print("*** ERROR: returned id %s doesn't match query %s" %(result['_id'],id))
    
    # successful result either:
    # {'ensembl.gene': 'ENSG00000149313', '_id': '60496', 'symbol': 'AASDHPPT'}
    # {'ensembl': [{'gene': 'ENSG00000275700'}, {'gene': 'ENSG00000276072'}], '_id': '26574', 'symbol': 'AATF'}
    print(result)
    ensembl_gene=[]; ensembl_proteins=[]
    if 'ensembl' in result:
        ensembl = result['ensembl']
        if isinstance(ensembl,list):
            for e in ensembl:
                gene, proteins = extract_ensembl_ids(id, e)
                
                if gene is None:  print("*** gene is None")
                else: ensembl_gene = join_as_lists(ensembl_gene,gene)
                
                if proteins is None: print("*** protein is None")
                else: ensembl_proteins = join_as_lists(ensembl_proteins,proteins)
                # eg: {'symbol': 'MAP3K14', 'entrezgene': 9020, 'ensembl': [{'gene': 'ENSG00000006062', 'protein': ['ENSP00000478552', 'ENSP00000480974', 'ENSP00000482657']}, {'gene': 'ENSG00000282637', 'protein': []}], '_id': '9020'}
            return ensembl_gene, ensembl_proteins
# Is it possible to have 
    return extract_ensembl_ids(id, result)  # return ensembl_gene, ensembl_proteins

    
def lookup_symbol(id):
    print("  Looking in MyGene for symbol:", id)
        
    # id = 'ERBB2'
    # id = 'RP4.592A1.2'
    # result = mg.getgene(id, fields="ensembl.protein, symbol, ensembl.gene, entrezgene", email="sbridgett@gmail.com")
    result = mg.query('symbol:'+id, species='human', fields="ensembl.protein, symbol, ensembl.gene, entrezgene, HGNC", email="sbridgett@gmail.com")
    # eg: mg.query('symbol:cdk2', species='human')
    # print(result)
    # eg: 
    #    {'total': 1, 'hits': [{'_id': '2064', 'symbol': 'ERBB2', 'ensembl': {'gene': 'ENSG00000141736', 'protein': ['ENSP00000269571', 'ENSP00000385185', 'ENSP00000404047', 'ENSP00000446466', 'ENSP00000462024', 'ENSP00000462270', 'ENSP00000462438', 'ENSP00000462808', 'ENSP00000463002', 'ENSP00000463427', 'ENSP00000463714', 'ENSP00000463719', 'ENSP00000464252', 'ENSP00000464420']}}], 'max_score': 91.26294, 'took': 11}
    # or if no hits:
    #    {'total': 0, 'took': 1, 'hits': [], 'max_score': None}
    
    #ensembl_gene = None
    #ensembl_proteins = None
    
    if result['total'] == 0:
        print("  No matches found in MyGene for symbol '%s'" %(id))
        return None,None,None
        # entrez_ids = ["1017","7248"]  
    else:
#        if result['_id'] != id:
#            print("*** ERROR: returned id %s doesn't match query %s" %(result['_id'],id))
    
    # successful result either:
    # {'ensembl.gene': 'ENSG00000149313', '_id': '60496', 'symbol': 'AASDHPPT'}
    # {'ensembl': [{'gene': 'ENSG00000275700'}, {'gene': 'ENSG00000276072'}], '_id': '26574', 'symbol': 'AATF'}
                
        print(result)
        entrez_id = None
        if '_id' in result:
            entrez_id = str(result['_id'])
        if 'entrezgene' in result:
            if str(result['entrezgene']) != entrez_id:
                print("entrezgene:", result['entrezgene'], "doesn't match request:",entrez_id)
            
        if 'hits' in result:
            ensembl_gene=[]; ensembl_proteins=[]
            for hit in result['hits']:
                gene,proteins = extract_ensembl_ids(id, hit)  # return ensembl_gene, ensembl_proteins
                if gene is None:  print("*** gene is None")
                else: ensembl_gene = join_as_lists(ensembl_gene,gene)                
                if proteins is None:  print("*** protein is None")
                else: ensembl_proteins = join_as_lists(ensembl_proteins,proteins)                

            return ensembl_gene, ensembl_proteins, entrez_id

        return extract_ensembl_ids(id, result), entrez_id  # return ensembl_gene, ensembl_proteins

# sys.exit()




symbol_to_stringdb = dict()
def load_stringdb_protein_alias_file_into_sqlite_db():
  print("Loading StringDB Protein alias into sqlite db ...")
  # *** A very good Sqlite & Python: https://pymotw.com/2/sqlite3/
  
  # A good article on SQLite and python:  http://sebastianraschka.com/Articles/2014_sqlite_in_python_tutorial.html
  # SQLite docs: https://www.sqlite.org/lang_createtable.html
  # more: http://www.askingbox.com/info/sqlite-creating-an-index-on-one-or-more-columns
  # http://zetcode.com/db/sqlitepythontutorial/
  # https://docs.python.org/3/library/sqlite3.html
  
  conn = sqlite3.connect('db_symbol_to_string_protein.sqlite3')
  c = conn.cursor()
  """
  #c.execute('''CREATE TABLE alias_to_stringdb (alias text PRIMARY KEY, string_protein text, source text)''') # Create table
  # OR:
  c.execute('''DROP TABLE alias_to_stringdb''')
  c.execute('''CREATE TABLE alias_to_stringdb (alias text, string_protein text, source text)''') # Create table
  c.execute('''CREATE INDEX alias_to_stringdb_index ON alias_to_stringdb(alias)''') # This isn't a UNIQUE index, as alias names might not be unique.

  rows = []
  row_count = 0
  total_row_count = 0  
  with open(protein_alias_file) as f:
    head = f.readline() # Skip header line
    for line in f:
      # alternatively use: line.replace('.',"\t").split("\t")  or: import re; re.split([.\t], line)
      string_protein, alias, source = line.rstrip("\r\n").split("\t")
      species, string_protein = string_protein.split('.') # Remove species (always is human 9606)
 
      # c.execute("INSERT INTO alias_to_stringdb VALUES (?, ?, ?)", (alias, string_protein, source)) # Insert a row of data.
      rows.append((alias, string_protein, source))
      row_count += 1
      total_row_count+=1

      if row_count == 1000: # commit each thousand.
        c.executemany('INSERT INTO alias_to_stringdb VALUES (?,?,?)', rows) # Insert many records at a time.
        rows = []
        row_count = 0
           
  if row_count > 0: # Add any remaining rows:
    c.executemany('INSERT INTO alias_to_stringdb VALUES (?,?,?)', rows)
    rows = []

  conn.commit()  # Save (commit) the changes
  """
  # for row in c.execute("SELECT * FROM alias_to_stringdb WHERE alias = ?", ('ARID1A',)):
  #for row in c.execute("SELECT * FROM alias_to_stringdb WHERE alias = ?", ('8343',)):
  for row in c.execute("SELECT * FROM alias_to_stringdb WHERE alias = ?", ('8289',)):
     # 8289 is entrez_id for 'HIST1H2BF';
     # 8343 is entrz_id for 'ARID1A': http://www.ncbi.nlm.nih.gov/gene/8289
  # for row in c.execute('SELECT * FROM alias_to_stringdb WHERE alias LIKE ?', ('ARID1A%',)): # startswith
    print(row)

  conn.close()  # We can also close the connection if we are done with it.- Just be sure any changes have been committed or they will be lost.

 
# books = Book.objects.filter(title__startswith=query)
# or
#__iexact=
#__startswith=query
#__istartswith=  # is: SELECT ... WHERE headline ILIKE 'Will%';

#      if entrez in entrez_to_stringdb:
#        print("Error: in stringdb duplicated entrez id:",entrez)
#      else:
#        entrez_to_stringdb[entrez] = string_protein
#      if  entrez in stringdb_to_entrez:
#        print("Error: duplicated string_protein:",string_protein)
#      else:    
#        stringdb_to_entrez[string_protein] = entrez

  print("Read %d entrez to stringdb lines" %(len(entrez_to_stringdb)))

  

# or could use pandas and read into a dataframe, eg: 
# from http://stackoverflow.com/questions/23057219/how-to-convert-csv-to-dictionary-using-pandas
#  dic = pd.Series.from_csv(filename, names=cols, header=None).to_dict()

# Read in the entrez to stringdb id mapping:
entrez_to_stringdb = dict()
stringdb_to_entrez = dict() # And the reverse with will be ensembl proteins as the keys
def load_entrez_to_stringdb_dictionary():
  print("Loading Entrez to StringDB dictionary ...")
  with open(entrez_to_stringdb_protein_ids_input_file) as f:
    head = f.readline() # Skip header line
    for line in f:
      # alternatively use: line.replace('.',"\t").split("\t")  or: import re; re.split([.\t], line)
      entrez, string_protein = line.rstrip("\r\n").split("\t")
      species, string_protein = string_protein.split('.') # Remove species (always is human)
      if entrez in entrez_to_stringdb:
        print("Error: in stringdb duplicated entrez id:",entrez)
      else:
        entrez_to_stringdb[entrez] = string_protein
      if  entrez in stringdb_to_entrez:
        print("Error: duplicated string_protein:",string_protein)
      else:    
        stringdb_to_entrez[string_protein] = entrez

  print("Read %d entrez to stringdb lines" %(len(entrez_to_stringdb)))


#mg = mygene.MyGeneInfo()
#fields = mg.get_fields()
#for k in fields: print("\n",k,fields[k])
#sys.exit()

# For some reason, firefox does display entrez results, but chrome gives error message: http://www.ncbi.nlm.nih.gov/gene/8339
# "
# Bad Request
#
# Your browser sent a request that this server could not understand.
# Size of a request header field exceeds server limit.
# Cookie
# /n"

# Showing stringdb results:
#    http://string-db.org/version_10/newstring_cgi/show_network_section.pl?all_channels_on=1&identifier=9606.ENSP00000321744



def add_ensembl_proteins_to_Gene_table_in_db():
  # Scan trough the Gene table:
  print("Adding Ensembl protein Ids to the Gene table ...")
  count_empty = 0
  count_not_found = 0
  count_found = 0
  driver_count_not_found = 0
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
    for g in Gene.objects.all().iterator():
      #print(g.gene_name,"   ",g.entrez_id)
      driver_text = '*DRIVER*' if g.is_driver else ''
      if g.entrez_id is None or g.entrez_id == '':
          print("Entrez Id is empty for %s gene %s" %(driver_text, g.gene_name))
          count_empty += 1
          if g.is_driver: driver_count_not_found += 1
          e_genes,e_proteins,entrez = lookup_symbol(g.gene_name)
          if e_proteins is not None:
              if isinstance(e_proteins,str):
                  e_proteins = [e_proteins,]
              print(e_proteins)                    
              for p in e_proteins:
                if p in stringdb_to_entrez:
                    print("***** %s symbol '%s' protein %s found in stringdb_to_entrez with entrez id %s" %(driver_text,g.gene_name,p,stringdb_to_entrez[p]))
          
          # result = mg.getgene(entrez_id, fields="ensembl.gene, symbol, ensembl.gene", email="sbridgett@gmail.com")  # use entrez gene id (string or integer) OR ensembl gene id.
          print("")
      else:
          # continue
          ensembl_protein_id = entrez_to_stringdb.get(g.entrez_id, None)
          if ensembl_protein_id is None:
              print("Error: for %s '%s' entrez id '%s' NOT found in entrez_to_stringdb map" %(driver_text,g.gene_name,g.entrez_id))
              count_not_found += 1
              if g.is_driver: driver_count_not_found += 1
              e_genes,e_proteins = lookup_entrez_id(g.entrez_id)
              if e_proteins is not None:
                if isinstance(e_proteins,str):
                  e_proteins = [e_proteins,]
                print(e_proteins)  
                for p in e_proteins:
                  if p in stringdb_to_entrez:
                    print("***** %s %s: entrez '%s' protein %s found in stringdb_to_entrez with entrez '%s'" %(driver_text,g.gene_name,g.entrez_id,p,stringdb_to_entrez[p]))
              
              print("")
          else:
              g.ensembl_protein_id = ensembl_protein_id
              g.save()
              count_found += 1

  print("Empty: %d,  Not_found: %d, Driver_count_not_found: %d,  Found: %d" %(count_empty, count_not_found, driver_count_not_found, count_found))
  
  
# ======
gendep_gene_protein_id_dict = dict()
def add_ensembl_proteins_from_sqlitedb_to_Gene_table_in_db():
  # Scan trough the Gene table:
  print("Adding Ensembl protein Ids to the Gene table ...")
  conn = sqlite3.connect('db_symbol_to_string_protein.sqlite3')
  c = conn.cursor()
  
  # As the SELECT .... LIKE ... is non-case sensitive, then need to create a NOCASE index otherwise very slow:  
  # c.execute('''CREATE INDEX nocase_alias_to_stringdb_index ON alias_to_stringdb(alias COLLATE NOCASE)''')
    
  count_empty = 0
  count_not_found = 0
  count_found = 0
  count_protein_ids_differ = 0
  count_multiple_protein_ids = 0
  driver_count_not_found = 0
  driver_count_multiple_protein_ids = 0
  count_entrez_not_found = 0
  
  protein_dict = dict()
  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
    for g in Gene.objects.all().iterator():      
      #print(g.gene_name,"   ",g.entrez_id)
      driver_text = '*DRIVER*' if g.is_driver else ''
      protein_id_from_entrez_id = ''
      
      if g.entrez_id is not None and g.entrez_id != '':
        rows = c.execute("SELECT * FROM alias_to_stringdb WHERE alias = ?", (g.entrez_id,)).fetchall()
        # columns are: alias, string_protein, source
        if len(rows) == 0:
          print("\nEntrez_id %s NOT found for %s %s" %(g.entrez_id,driver_text,g.gene_name))
          count_entrez_not_found += 1
        elif len(rows) == 1:
          protein_id_from_entrez_id = rows[0][1]
        else:
           print("For %s %s Multiple protein_id_from_entrez_id %s:" %(driver_text,g.gene_name,g.entrez_id))
           print(rows)
           
      rows = c.execute("SELECT * FROM alias_to_stringdb WHERE alias = ?", (g.gene_name,)).fetchall()
      # columns are: alias, string_protein, source
      
      if len(rows) == 0:
        print("\nAlias NOT found for %s %s" %(driver_text,g.gene_name))
        count_not_found += 1
        if g.is_driver: driver_count_not_found += 1
        rows = c.execute('SELECT * FROM alias_to_stringdb WHERE alias LIKE ?', (g.gene_name+'%',)).fetchall()
        if len(rows)>0: print("  BUT found %d LIKE it: %s" %(len(rows), rows))
        
      elif len(rows) == 1:
        if protein_id_from_entrez_id!='' and protein_id_from_entrez_id!=rows[0][1]:
          print("\nWarning: %s %s protein_id %s from entrez_id different than from gene_name: %s" %(driver_text,g.gene_name, protein_id_from_entrez_id,rows[0][1]))
        if g.ensembl_protein_id is None or g.ensembl_protein_id == '':
          g.ensembl_protein_from_alias_table = True
          g.ensembl_protein_id = rows[0][1]
          g.save()
          count_found += 1
        elif rows[0][1] != g.ensembl_protein_id: # check if is same as that already added due to the entrez_id
          print("\nWarning: %s protein_ids differ: was: %s new: %s" %(driver_text,g.ensembl_protein_id,rows[0][1]))
          count_protein_ids_differ += 1
        # else is same so don't need to do anything.
        
      else: # rows > 1
        # see if the aliases string_proteins are all the same - could add a distinct(string_protein) on sql in postegres
        protein_dict.clear()          # or could use a set.
        for alias,protein,source in rows:
          protein_dict[protein] = True
        if len(protein_dict) == 1:
          g.ensembl_protein_from_alias_table = True
          g.ensembl_protein_id = protein_dict.keys()[0]
          g.save()        
        else:
          print("\nFor %s %s several string_proteins: %s" %(driver_text,g.gene_name, protein_dict.keys()))
          print(rows)
          
          if protein_id_from_entrez_id in protein_dict:
            print("  but for %s %s GOOD NEWS: protein_id_from_entrez %s is one of these" %(driver_text,g.gene_name,protein_id_from_entrez_id))
            g.ensembl_protein_id = protein_id_from_entrez_id
            g.save()

          else:
            count_multiple_protein_ids += 1
            if g.is_driver: driver_count_multiple_protein_ids += 1
            
      gendep_gene_protein_id_dict[g.ensembl_protein_id] = True # Used later to only load interactions that have protein_ids in the gene table.
      
     # 8289 is entrez_id for 'HIST1H2BF';
     # 8343 is entrz_id for 'ARID1A': http://www.ncbi.nlm.nih.gov/gene/8289
  # for row in c.execute('SELECT * FROM alias_to_stringdb WHERE alias LIKE ?', ('ARID1A%',)): # startswith



      """  
      if g.entrez_id is None or g.entrez_id == '':
          print("Entrez Id is empty for %s gene %s" %(driver_text, g.gene_name))
          count_empty += 1
          if g.is_driver: driver_count_not_found += 1
          e_genes,e_proteins,entrez = lookup_symbol(g.gene_name)
          if e_proteins is not None:
              if isinstance(e_proteins,str):
                  e_proteins = [e_proteins,]
              print(e_proteins)                    
              for p in e_proteins:
                if p in stringdb_to_entrez:
                    print("***** %s symbol '%s' protein %s found in stringdb_to_entrez with entrez id %s" %(driver_text,g.gene_name,p,stringdb_to_entrez[p]))
          
          # result = mg.getgene(entrez_id, fields="ensembl.gene, symbol, ensembl.gene", email="sbridgett@gmail.com")  # use entrez gene id (string or integer) OR ensembl gene id.
          print("")
      else:
          # continue
          ensembl_protein_id = entrez_to_stringdb.get(g.entrez_id, None)
          if ensembl_protein_id is None:
              print("Error: for %s '%s' entrez id '%s' NOT found in entrez_to_stringdb map" %(driver_text,g.gene_name,g.entrez_id))
              count_not_found += 1
              if g.is_driver: driver_count_not_found += 1
              e_genes,e_proteins = lookup_entrez_id(g.entrez_id)
              if e_proteins is not None:
                if isinstance(e_proteins,str):
                  e_proteins = [e_proteins,]
                print(e_proteins)  
                for p in e_proteins:
                  if p in stringdb_to_entrez:
                    print("***** %s %s: entrez '%s' protein %s found in stringdb_to_entrez with entrez '%s'" %(driver_text,g.gene_name,g.entrez_id,p,stringdb_to_entrez[p]))
              
              print("")
          else:
              g.ensembl_protein_id = ensembl_protein_id
              g.save()
              count_found += 1
      """

  conn.close()  # We can also close the connection if we are done with it.- Just be sure any changes have been 
  print("Empty: %d,  Not_found: %d, Driver_count_not_found: %d,  Found: %d, count_protein_ids_differ: %d,  count_multiple_protein_ids: %d, driver_count_multiple_protein_ids: %d, count_entrez_not_found: %d" %(count_empty, count_not_found, driver_count_not_found, count_found, count_protein_ids_differ, count_multiple_protein_ids, driver_count_multiple_protein_ids,count_entrez_not_found))
  
# RP4-592A1.2-001	ENST00000427762	690	No protein  


# To reduce memory usage, as all links occur twice (a p1 p2 and as p2 p1, just need to read p1 p2 and can ignore the other and test both ways later)
p1p2_dict = dict()
def load_stringdb_protein_interaction_file_into_dictionary():
  print("Loading StringDB protein interactions into dictionary ...")
  if len(gendep_gene_protein_id_dict) == 0:
     print("**** ERROR: Need to load gendep_gene_protein_id dictionary first")
     exit()
  
  min_score_to_load = 400 # To reduce memory usage
  dict_count = 0
  rev_count =0

  with open(protein_interaction_input_file) as f:
    head = f.readline()
    for line in f:
      p1, p2, score = line.split(' ')
      score = int(score)
      #if score < min_score_to_load: continue
      species, p1 = p1.split('.')
      species, p2 = p2.split('.')
      if p1 not in gendep_gene_protein_id_dict or p2 not in gendep_gene_protein_id_dict:
        continue  # Only need to load interactions for genes in our cgdd gendep_gene table.
      rev_key = p2+'_'+p1
      if rev_key in p1p2_dict: # check score is same.
        if p1p2_dict[rev_key] == score: rev_count+=1
        else: print("*** ERROR: Score %s != %s is different for reversed key %s" %(p1p2_dict[rev_key],score,rev_key))
      else:
        key = p1+'_'+p2
        p1p2_dict[key] = score
        dict_count += 1       
         #print("Reversed found",rev_key)
  if rev_count != dict_count: print("p1p2_dict: rev_count %d != dict_count %d" %(rev_count, dict_count))
  print("dict_count:", dict_count) # rev_count: 4274001
 
#     if dict_num<1000:
#        key = p1+'_'+p2
#        p1p2_dict[key] = None
#        dict_num += 1
     # if int(score) >= 700:
     #  if p2 != last:
     #    count+=1
     #    last = p2 # but not ordered on p2 so need a hash
   
   # Only consider as interaction if score >= 700


#print("Number with score>=700:",count)
# $ ./add_ensembl_proteinids_and_stringdb.py
# Number with score>=700: 642304


# Number unique p1 with score>=700: 15554

# So fastest is to creat hash in memory of my gene/dependency table then search this as read in these rows.
# or if hash these ?


def add_interaction_scores_to_dependency_table_in_db():
  if len(p1p2_dict) == 0:
     print("*****ERROR: p1p2_dict is EMPTY - need to load it first ******")
     exit()
     
  print("Adding interaction scores to the Dependency table ...")
  count_dependencies = 0
  count_have_both_protein_ids = 0
  count_all_in_stringdb = 0
  count_medium = 0
  count_high = 0
  count_highest = 0
#  count_found = 0
#  count_not_found = 0
  count_has_interaction = 0
  count_no_interaction = 0

  with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
    for d in Dependency.objects.all().iterator():
      count_dependencies += 1
      #print(d.driver_id,"   ",d.target_id)
      # if g.entrez_id is None or g.entrez_id == '':
      driver_protein = d.driver.ensembl_protein_id
      target_protein = d.target.ensembl_protein_id
      if driver_protein is None or driver_protein == '' or target_protein is None or target_protein =='':
        continue
      count_have_both_protein_ids += 1
      score = 0  
      key = driver_protein+'_'+target_protein
      if key in p1p2_dict:
          score = p1p2_dict[key]
          count_all_in_stringdb += 1
      else:
          key = target_protein+'_'+driver_protein # Need to check the reverse key as only loading p1 p2, not p2 p1 keys to save memory.
          if key in p1p2_dict:
              score = p1p2_dict[key]
              count_all_in_stringdb += 1
              
#      if score >=400 or driver_protein == target_protein:  # The p1p2_dict only contains 
#           d.interaction = True  # As column is currently set to NullBoolean.
#           count_has_interaction += 1
#      else:
#           d.interaction = False  # The rows with empty protein id will be left as null.
#           count_no_interaction += 1

# In future when change interaction to a CharField, use:           
      if score >=900 or driver_protein == target_protein:    # self interaction marked as 'Highest' as Colm suggested: "can you mark any interaction where the driver and target are the same gene as 'Highest'? For example KRAS has a dependency upon KRAS & ERBB2 has a dependency upon ERBB2"
           d.interaction = 'Highest' # was: 'd.interaction_hhm'
           count_highest += 1
      elif score >=700:
           d.interaction = 'High'
           count_high += 1
      elif score >=400:
           d.interaction = 'Medium'
           count_medium += 1
      else:
           count_no_interaction += 1
      d.save()

  count_has_interaction = count_medium + count_high + count_highest
  
  print("count_dependencies: %d,  count_have_both_protein_ids: %d,  count_all_in_stringdb: %d" %(count_dependencies, count_have_both_protein_ids,count_all_in_stringdb))
  print("count_has_interaction: %d, count_no_interaction: %d" %(count_has_interaction, count_no_interaction))
  print("count_medium: %d,  count_high: %d,  count_highest: %d" %(count_medium, count_high, count_highest))
# Found: count_medium: 681,  count_high: 234,  count_highest: 381


#### The following is already done in load_data.py
#def merge_prevnames_and_synonyms():
  #with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
#    for g in Gene.objects.all():  # .iterator()
#      g.prevnames_synonyms = g.prev_names + ('' if g.prev_names == '' or g.synonyms == '' else '|') + g.synonyms
#      #print(g.prevnames_synonyms)
#      g.save()

      
if __name__ == "__main__":
    # load_stringdb_protein_alias_file_into_sqlite_db()
    
    #### merge_prevnames_and_synonyms()
    
    # Still needed to rebuild table:
    add_ensembl_proteins_from_sqlitedb_to_Gene_table_in_db()
    
    # load_entrez_to_stringdb_dictionary()   
    # add_ensembl_proteins_to_Gene_table_in_db()

    # Both needed to rebuild table ### (11 April 2016):
    load_stringdb_protein_interaction_file_into_dictionary()
    add_interaction_scores_to_dependency_table_in_db()
    print("Finished")

# sys.exit()
    
"""
****Found these additional mappings:
$ grep '\*\*\*\*' Retrieving_Ensembl_ids.txt
***** 'SGK494' protein ENSP00000301037 found in stringdb_to_entrez
***** '8347' protein ENSP00000321744 found in stringdb_to_entrez with entrez '8339'
***** '728441' protein ENSP00000248923 found in stringdb_to_entrez with entrez '2678'
***** '728458' protein ENSP00000358945 found in stringdb_to_entrez with entrez '2652'
***** 'KIAA1804' protein ENSP00000355583 found in stringdb_to_entrez
***** '728635' protein ENSP00000326219 found in stringdb_to_entrez with entrez '317749'
***** 'HDGFRP3' protein ENSP00000299633 found in stringdb_to_entrez
***** '653220' protein ENSP00000364766 found in stringdb_to_entrez with entrez '653219'
***** '728945' protein ENSP00000358224 found in stringdb_to_entrez with entrez '164022'
***** '10901' protein ENSP00000326219 found in stringdb_to_entrez with entrez '317749'
***** '9103' protein ENSP00000271450 found in stringdb_to_entrez with entrez '2212'
***** '653192' protein ENSP00000272395 found in stringdb_to_entrez with entrez '129868'
***** '7637' protein ENSP00000331465 found in stringdb_to_entrez with entrez '100996464'
"""


