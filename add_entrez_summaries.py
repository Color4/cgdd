#!/usr/bin/env python

""" Script to add the retrieve the Entrez summaries using Entrez EUtils, and add these sumamries to the database Gene table """

import sys, os
import requests
from urllib.request import Request, urlopen
from urllib.error import URLError
import xml.etree.ElementTree as ET

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cgdd.settings")
import django
django.setup()

from gendep.models import Gene


ALWAYS_UPDATE_GENE_TABLE = False  # False means don't update g.ncbi_summary if already has an existing summary (which was from Entrez full details)


# https://docs.python.org/3.5/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.find

# XML parsing: There is a "gotcha" with the find() method that will eventuallyit bite you: In a boolean context, ElementTree element objects will evaluate to False if they contain no children (i.e. if len(element) is 0). This means that if element.find('...') is not testing whether the find() method found a matching element; it's testing whether that matching element has any child elements! To test whether the find() method returned an element, use if element.find('...') is not None.
   # from: http://www.diveintopython3.net/xml.html


EUTILS_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

# epost.fcgi?db=gene&id=7173,22018,54314,403521,525013

# Main info:  http://www.ncbi.nlm.nih.gov/books/NBK25500/#chapter1.Downloading_Document_Summaries
# http://www.ncbi.nlm.nih.gov/books/NBK25501/

# Python Exception handling:
#    https://doughellmann.com/blog/2009/06/19/python-exception-handling-techniques/

# Ensembl REST API:  http://rest.ensembl.org/
#   https://www.biostars.org/p/70387/

# http://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.EPost__ESummaryEFetch
# Download protein records corresponding to a list of GI numbers.
"""
$db = 'protein';
$id_list = '194680922,50978626,28558982,9507199,6678417';

#assemble the epost URL
$base = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/';
$url = $base . "epost.fcgi?db=$db&id=$id_list";

#post the epost URL
$output = get($url);

#parse WebEnv and QueryKey
$web = $1 if ($output =~ /<WebEnv>(\S+)<\/WebEnv>/);
$key = $1 if ($output =~ /<QueryKey>(\d+)<\/QueryKey>/);

### include this code for EPost-ESummary
#assemble the esummary URL
$url = $base . "esummary.fcgi?db=$db&query_key=$key&WebEnv=$web";

#post the esummary URL
$docsums = get($url);
print "$docsums";

### include this code for EPost-EFetch
#assemble the efetch URL
$url = $base . "efetch.fcgi?db=$db&query_key=$key&WebEnv=$web";
$url .= "&rettype=fasta&retmode=text";

#post the efetch URL
$data = get($url);
print "$data";
**** Note: To post a large number (more than a few hundred) UIDs in a single URL, please use the HTTP POST method for the EPost call (see Application 4).
"""
# http://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.Application_3_Retrieving_large


#### *** Can create more complex queies using brackets:
### http://www.ncbi.nlm.nih.gov/books/NBK3837/
# eg: 	alive[prop] AND transporter[title] AND ("Drosophila melanogaster"[orgn] OR "Mus musculus"[orgn])
# http://www.ncbi.nlm.nih.gov/Class/MLACourse/Modules/Entrez/complex_boolean.html

### Good tips & tricks for Entrez searches: http://biochem.uthscsa.edu/~hs_lab/frames/molgen/tutor/Entrez2.html


# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi?db=gene&id=1&WebEnv=NCID_1_63346644_130.14.18.34_9001_1462830382_986530756_0MetA0_S_MegaStore_F_1

# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=1


# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/egquery.fcgi?term=mouse[orgn]

# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=ERBB2[GENE]+AND+9606[TID]
#+AND+breast+cancer+AND+2008[pdat]&usehistory=y


# List of search terms that can be used: http://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=gene

# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=ERBB2[GENE]+AND+9606[TID]
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term=VEGFA[GENE]+AND+9606[TID]

# for the full gene record, use efetch, and retmode:
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=2&retmode=xml
# More details: http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.EFetch


# Retrieve gene information:
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=1,2
#&usehistory=y

#http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=2&retmode=xml
#asn.1, default

# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=2064,7422

# As well as seraching by [GENE], could search by: [PREF] ( Preferred symbol of the gene )

#$esearch_result =~ 
#  m|<Count>(\d+)</Count>.*<QueryKey>(\d+)</QueryKey>.*<WebEnv>(\S+)</WebEnv>|s;

#tree = ET.parse('test_country_data.xml')

def get_entrez_ids():
  tree = ET.parse('test_entrez_geneid.xml')
  root = tree.getroot()
  #root = ET.fromstring(country_data_as_string)
  for child in root:
   if child.tag=="IdList":
      print(child.tag, child.attrib)
      for id in child.findall('Id'):
         print(id.text)


def test_post():   
   url = EUTILS_URL+"esummary.fcgi?db=gene"
   data = {'id': '2064,7422'}
   
   # ...    $req->content_type(); 
   #headers = {'content-type': 'application/x-www-form-urlencoded'}   
   
   r = requests.post(url, headers=headers, data=data) # insead of ...get(...)   
   r.raise_for_status()  # print(r.status_code == requests.codes.ok)
   print(r.text)
   
   #print(r.encoding)
   #print(r.headers)
   #gene_summaries_found_count = 0
   
   #fout1.write(r.text)
   #fout1.write("\nEND\n")   

    # ...    $req->content_type('application/x-www-form-urlencoded'); 
    
    #&id=$id
          
         
def get_entrez_summaries(entrez_to_genename_dict, fout1, fout2):

    # Minimizing the Number of Requests: If a task requires searching for and/or downloading a large number of records, it is much more efficient to use the Entrez History to upload and/or retrieve these records in batches rather than using separate requests for each record. Please refer to Application 3 in Chapter 3 for an example. Many thousands of IDs can be uploaded using a single EPost request, and several hundred records can be downloaded using one EFetch request.   http://www.ncbi.nlm.nih.gov/books/NBK25497/
    # First use ESearch to retrieve the GI numbers for these sequences and post them on the History server, then use multiple EFetch calls to retrieve the data in batches of 500.
    
    # see: http://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.Application_4_Finding_unique_se
    
    # eg: $url = $base . "epost.fcgi?db=$db&id=$id_list";   

   url = EUTILS_URL+"esummary.fcgi?db=gene"   
   data = {'id': ",".join(entrez_to_genename_dict.keys())}
   headers = {"Content-Type": "application/x-www-form-urlencoded"}
   
   r = requests.post(url, headers=headers, data=data) # insead of:  r = requests.get(url) 
      
   r.raise_for_status()  # print(r.status_code == requests.codes.ok)
   #print(r.encoding)
   #print(r.headers)
   gene_summaries_found_count = 0
   
   fout1.write(r.text)
   fout1.write("\nEND\n")

   root = ET.fromstring(r.text) # root is 'eSummaryResult'
   # OR to read from file: tree = ET.parse('test_entrez_summary.xml'); root=tree.getroot()
   for docsumset in root.findall('DocumentSummarySet'):
     #print(docsumset.tag, docsumset.attrib, docsumset.text)
     if docsumset.attrib['status'] != "OK":
        print("ERROR: DocSum status: ",docsumset.attrib['status'])
     for doc in docsumset.findall('DocumentSummary'):
        entrez_id = doc.attrib['uid']
        gene_name = None
        summary = None
        aliases = None
        for d in doc:
            if d.tag=="Name":
                if gene_name is None:
                    gene_name = d.text
                else:
                    print("*** WARNING: Already found a gene name '%s' and now '%s' for entrez_id %s" %(gene_name,d.text,entrez_id))

            #elif d.tag=="Description":
            #   print(d.tag,d.text)
            #elif d.tag=="Status":
            #   print(d.tag,d.text)

            elif d.tag=="Summary" and d.text!=None:
                summary=d.text.rstrip()
             
            elif d.tag=="OtherAliases":
                aliases=d.text # eg: CD334, JTK2, TKF
           
        if summary is None:
            print(gene_name+"\t"+entrez_id+"\tNone")
        else:
            if gene_name is None:
                print("*** ERROR: gene_name NOT found yet ***")
                gene_name=entrez_to_genename_dict[entrez_id]
                
            elif gene_name != entrez_to_genename_dict[entrez_id]:
                if aliases is None:
                    print("*** ERROR: Gene_name mismatch '%s' '%s' and no Aliases ***" %(gene_name, entrez_to_genename_dict[entrez_id]))
                elif gene_name not in aliases.split(', '):
                    print("*** ERROR: Gene_name mismatch '%s' '%s' and *NOT* in Aliases: '%s' ***" %(gene_name, entrez_to_genename_dict[entrez_id], aliases))
                gene_name=entrez_to_genename_dict[entrez_id]
                 
            g2 = Gene.objects.get(gene_name=gene_name)
            if g2.entrez_id != entrez_id:
                print("*** ERROR: Entrez_id Mismatch '%s' '%s' ***" %(entrez_id, g2.entrez_id))
            else:
                print(gene_name+"\t"+entrez_id+"\t"+summary)
                g2.ncbi_summary = summary
                g2.save()
                fout2.write(gene_name+"\t"+entrez_id+"\t"+summary)
                gene_summaries_found_count += 1
           #   print(d.tag,d.text)
            #print(d.tag,d.text)

                
   #genes_without_summaries = []
   return gene_summaries_found_count

 # This script did rely on Name appearing before Summary in the XML. Otherwise use doc.find('Name') above, then doc.find('Summary')   
   
"""
<eSummaryResult>
   <DocumentSummarySet status="OK">
     <DbBuild>Build160509-0315m.1</DbBuild>
     <DocumentSummary uid="2064">
        <Name>ERBB2</Name>
        <Description>erb-b2 receptor tyrosine kinase 2</Description>
        <Status>0</Status>
        <Summary>This gen........
        <OtherAliases>CD340, HER-2, HER-2/neu, HER2, MLN 19, NEU, NGL, TKR1</OtherAliases>
        <NomenclatureSymbol>ERBB2</NomenclatureSymbol>     
        etc...
"""
# Currently, the ElementTree module skips over any XML comments, processing instructions, and document type declarations in the input.



def process_all_genes_in_db():
 BATCH_SIZE=2000 # number of ids to submit in one query.
 genes_without_entrez_ids = []
 genes_without_summary = []
 entrez_to_genename_dict = dict()

 genes_processed_count = 0
 genes_to_be_updated_count = 0
 total_gene_summaries_found_count = 0

 fout1 = open( "entrez_gene_summaries.xml","w")
 fout2 = open("entrez_gene_summaries.txt","w")
 fout2.write("Gene_name\tEntrez_id\tSummary\n")

 with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
  for g in Gene.objects.all().iterator():
    #print(g.gene_name, g.entrez_id)
    if g.entrez_id=='' or g.entrez_id=='NoEntrezId':
        genes_without_entrez_ids.append(g.gene_name)
    elif ALWAYS_UPDATE_GENE_TABLE or g.ncbi_summary is None or g.ncbi_summary == '':
        entrez_to_genename_dict[g.entrez_id] = g.gene_name
        genes_to_be_updated_count += 1
        
    #driver_text = '*DRIVER*' if g.is_driver else ''
    genes_processed_count += 1
    
    # Request 100 interactions at a time, to reduce load on server
    if len(entrez_to_genename_dict) == BATCH_SIZE:
      total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

#      unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
           # print("GENE:\t%s\t%s" %(gene_name,entrez_summaries[entrez_id]))

#           genes_with_summary_count += 1
#        else:
#           genes_without_summary.append(gene_name)        
      entrez_to_genename_dict.clear()
        
      #print("genes_processed_count:", genes_processed_count)
      
  if len(entrez_to_genename_dict) > 0: # Process any remaining genes as < BATCH_SIZE
    total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

 fout1.close()
 fout2.close()
    
 print("Genes_processed: %d,  Genes_to_be_updated: %d,  Gene_summaries_found: %d" %(genes_processed_count, genes_to_be_updated_count, total_gene_summaries_found_count))
 print("\nGenes_without_entrez_ids: %d:" %(len(genes_without_entrez_ids)) )
 print("\n".join(genes_without_entrez_ids))

      #gene_count = 0




if __name__ == "__main__":
    process_all_genes_in_db()
    #get_entrez_summaries({'2064':'ERBB2', '7422':'VEGFA'},None,None)
    
    #test_post()
