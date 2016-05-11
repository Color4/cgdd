#!/usr/bin/env python

import sys, os
from django.db import transaction
import mygene

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")
import django
django.setup()

from gendep.models import Gene # Dependency, Study, Removed: Histotype, Drug.


import requests
from urllib.request import Request, urlopen
from urllib.error import URLError
import json



# From: http://dgidb.genome.wustl.edu/api


# The preferred method for accessing this endpoint is a GET request, it will also accept POST requests to accomodate large gene lists if needed.
# http://dgidb.genome.wustl.edu

 
# http://dgidb.genome.wustl.edu/api/v1/interactions.json?interaction_types=inhibitor&genes=ERBB2,SMAD2
 
# interaction_types=inhibitor
# source_trust_levels=Expert%20curated
# interaction_sources=TTD,DrugBank
 
# Also:
#  drug_types=antineoplastic
  
#import urllib
"""
url = 'http://www.uniprot.org/mapping/'

params = {
'from':'ACC',
'to':'P_REFSEQ_AC',
'format':'tab',
'query':'P13368 P20806 Q9UM73 P97793 Q17192'
}
"""

#genes = []
#genes['genes'] = self.genes


def get_interactions(gene_list):
  url = "http://dgidb.genome.wustl.edu/api/v1/interactions.json?interaction_types=inhibitor&genes=" + ",".join(gene_list)
  r = requests.get(url)
  #print(r.status_code == requests.codes.ok)
  r.raise_for_status()
  #print(r.encoding)
  #print(r.headers)
  result = r.json()
  
  gene_drugs = dict()
  unmatched_terms = ''
  matches = result['matchedTerms']
  #if(matches):
       #print("gene_name\tdrug_name\tinteraction_type\tsource\tgene_categories")
  for match in matches:
            gene = match['geneName']
            gene_drugs[gene] = dict()
            #categories = match['geneCategories']
            #categories.sort()
            #joined_categories = ",".join(categories)
            for interaction in match['interactions']:
                #source = interaction['source']
                drug = interaction['drugName']
                gene_drugs[gene][drug] = True
                #interaction_type = interaction['interactionType']
                #print(gene + "\t" + drug + "\t" + interaction_type + "\t" + source + "\t" + joined_categories.lower())
  for unmatched in result['unmatchedTerms']:
            if unmatched_terms != '': unmatched_terms += ', '
            unmatched_terms += unmatched['searchTerm']
            print("Unmatched search term: " + unmatched['searchTerm'])
            print("Possible suggestions: " + ",".join(unmatched['suggestions']))
            
  for gene in gene_drugs:
    gene_drugs[gene] = ", ".join(sorted(gene_drugs[gene])) # or ", ".join(list(drugs[gene_gene].keys()))
    
  return gene_drugs, unmatched_terms

#genes = 'ERBB2,ERBB3'

# From: http://docs.python-requests.org/en/latest/user/quickstart/#json-response-content

genes_with_inhibitors_count = 0
#gene_count = 0
genes_processed = 0
gene_list = []
unmatched_genes = ''
with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
  for g in Gene.objects.all().iterator():
    print(g.gene_name)
    gene_list.append(g.gene_name)
    driver_text = '*DRIVER*' if g.is_driver else ''
    genes_processed += 1
    #gene_count += 1
    # Request 100 interactions at a time, to reduce load on server
    if len(gene_list) == 100:
      gene_drugs, unmatched = get_interactions(gene_list)      
      unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
      for gene_name in gene_drugs:
        g2 = Gene.objects.get(gene_name=gene_name)
        g2.inhibitors = gene_drugs[gene_name]
        g2.save()
        print("GENE:\t%s\t%s" %(gene_name,gene_drugs[gene_name]))
        genes_with_inhibitors_count += 1
      gene_list.clear()
      print("genes_processed:", genes_processed)
      
  if len(gene_list) > 0: # Process any remaining genes as < 100
    gene_drugs, unmatched = get_interactions(gene_list)      
    unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
    for gene_name in gene_drugs:
      g2 = Gene.objects.get(gene_name=gene_name)
      g2.inhibitors = gene_drugs[gene_name]
      g2.save()
      print("GENE:\t%s\t%s" %(gene_name,gene_drugs[gene_name]))      
      genes_with_inhibitors_count += 1      
    gene_list.clear()
    
print("genes_processed: %d,  genes_with_inhibitors_count: %d" %(genes_processed, genes_with_inhibitors_count))
print("unmatched_genes:",unmatched_genes)
      #gene_count = 0
      

"""
exit()

req = Request(url)
try:
        response = urlopen(req)
except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server:', e.reason)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request. Error code:', e.code)
else:  # everything is fine
# http://stackoverflow.com/questions/12965203/how-to-get-json-from-webpage-into-python-script

response = urlopen(url)
    data = str(response.read())
    return json.loads(data)
 or:
r = requests.get('someurl')
print r.json() # if response type was set to JSON, then you'll automatically have a JSON response here... 
    
        result = json.load(response.decode('utf-8'))  # whereas json.loads which consumes a string use (which is why .read()...
        print(result)
        #protein_dict2 = dict()
        #for line in response:
          # if line:
#==============================================          
#        self.request = DGIAPI.domain + DGIAPI.api_path
#        self.response = requests.post(self.request, data = self.payload)
        
#response = urllib.request.urlopen(request)
#obj = json.load(response)
#  response = json.loads(self.response.content)
"""


"""
data = urllib.urlencode(params)
request = urllib.request.Request(url, data)
contact = "" # Please set your email address here to help us debug in case of problems.
request.add_header('User-Agent', 'Python %s' % contact)
response = urllib2.urlopen(request)
page = response.read(200000)
"""


"""
From: http://dgidb.genome.wustl.edu/api/v1/interaction_types.json

[
"activator",
"adduct",
"agonist",
"allosteric modulator",
"antagonist",
"antibody",
"antisense",
"antisense oligonucleotide",
"binder",
"blocker",
"chaperone",
"cleavage",
"cofactor",
"competitive",
"immunotherapy",
"inducer",
"inhibitor",
"inhibitory allosteric modulator",
"inverse agonist",
"ligand",
"modulator",
"multitarget",
"n/a",
"negative modulator",
"other/unknown",
"partial agonist",
"partial antagonist",
"positive allosteric modulator",
"potentiator",
"product of",
"stimulator",
"suppressor",
"vaccine"
]
"""

"""
From: http://dgidb.genome.wustl.edu/api/v1/interaction_sources.json
[
"CIViC",
"CancerCommons",
"ChEMBL",
"ClearityFoundationBiomarkers",
"ClearityFoundationClinicalTrial",
"DoCM",
"DrugBank",
"GuideToPharmacologyInteractions",
"MyCancerGenome",
"MyCancerGenomeClinicalTrial",
"PharmGKB",
"TALC",
"TEND",
"TTD",
"TdgClinicalTrial"
]
"""

"""
From: http://dgidb.genome.wustl.edu/api/v1/drug_types.json
[
"antineoplastic",
"other"
]
"""

"""
From: http://dgidb.genome.wustl.edu/api/v1/source_trust_levels.json
[
"Expert curated",
"Non-curated"
]
"""


