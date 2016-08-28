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

"""
================
f = open('test.txt', 'r')
while True:
    line = f.readline()
    if (line == ''):
        break
    print "f.tell(): ",f.tell()


# If you need to rely on .tell(), don't use the file object as an iterator. You can turn .readline() into an iterator instead (at the price of some performance loss):
for line in iter(f.readline, ''):
    print f.tell()
  
    
http://stackoverflow.com/questions/14145082/file-tell-inconsistency
==== But the following reads big buffered block, so reports the wrong position
f = open('test.txt', 'r')
for line in f:
    print "f.tell(): ",f.tell()

================
"""


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






def get_entrez_full(entrez_to_genename_dict, fout1, fout2):

    # Minimizing the Number of Requests: If a task requires searching for and/or downloading a large number of records, it is much more efficient to use the Entrez History to upload and/or retrieve these records in batches rather than using separate requests for each record. Please refer to Application 3 in Chapter 3 for an example. Many thousands of IDs can be uploaded using a single EPost request, and several hundred records can be downloaded using one EFetch request.   http://www.ncbi.nlm.nih.gov/books/NBK25497/
    # First use ESearch to retrieve the GI numbers for these sequences and post them on the History server, then use multiple EFetch calls to retrieve the data in batches of 500.
    
    # see: http://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.Application_4_Finding_unique_se
    
    # eg: $url = $base . "epost.fcgi?db=$db&id=$id_list";   

   url = EUTILS_URL+"efetch.fcgi?db=gene" # Instead of "esummary.fcgi?db=gene"
   data = {'retmode':'xml', 'id': ",".join(entrez_to_genename_dict.keys())}  # Need to specify retmode of xml, otherwise returns asn.1, default
   headers = {"Content-Type": "application/x-www-form-urlencoded"}
   
   r = requests.post(url, headers=headers, data=data) # insead of:  r = requests.get(url) 
      
   r.raise_for_status()  # print(r.status_code == requests.codes.ok)
   #print(r.encoding)
   #print(r.headers)
   gene_summaries_found_count = 0
   
   fout1.write(r.text)
   fout1.write("\nEND\n")

   #root = ET.fromstring(r.text) # root is 'Entrezgene-Set'
   # OR to read from file:
   # tree = ET.parse('test_entrez_full.xml'); root=tree.getroot()
   tree = ET.parse('test_entrez_full2.xml'); root=tree.getroot()
   #tree = ET.parse('test_entrez_full_ERBB2.xml'); root=tree.getroot()   
   
   # Removed these two lines:
   # <?xml version="1.0" ?>
   # <!DOCTYPE Entrezgene-Set PUBLIC "-//NLM//DTD NCBI-Entrezgene, 21st January 2005//EN" "http://www.ncbi.nlm.nih.gov/data_specs/dtd/NCBI_Entrezgene.dtd">

     # print(entrezgene.tag, entrezgene.attrib, entrezgene.text)
#     if entrezgene.attrib['status'] != "OK":
#        print("ERROR: DocSum status: ",docsumset.attrib['status'])
   print("#START")
   for entrezgene in root.findall('Entrezgene'):  # repeats for each gene requested
     for entrezgene_track_info in entrezgene.findall('Entrezgene_track-info'):
       for gene_track in entrezgene_track_info.findall('Gene-track'):
         for gene_track_geneid in gene_track.findall('Gene-track_geneid'):
           entrez_id = gene_track_geneid.text
           print("Gene track entrez_id:",entrez_id)
                                 
         for gene_track_status in gene_track.findall('Gene-track_status'):
           gene_track_status_value = gene_track_status.attrib['value'] # != "live":    or 0
           gene_track_status_text = gene_track_status.text  # 0 or 1, etc
           
           print("Gene track_status value: '%s',  gene_track_status_text: '%s'" %(gene_track_status_value,gene_track_status_text) )
#           if gene_track_status_value != "live": print("Not live")  # 0</Gene-track_status>
            
#           <Gene-track_status value="secondary">1</Gene-track_status> - ie. replaced by new id.

         # *** Only if GeneId has changed:
         for gene_track_current_geneid in gene_track.findall('Gene-track_current-id'):
           for dbtag in gene_track_current_geneid.findall('Dbtag'):
             for dbtag_db in dbtag.findall('Dbtag_db'):
               dbtag_db_text = dbtag_db.text   # Locus or GeneID
             for dbtag_tag in dbtag.findall('Dbtag_tag'):
               for object_id in dbtag_tag.findall('Object-id'):
                 for object_id_id in object_id.findall('Object-id_id'):
                    print(dbtag_db_text+":",object_id_id.text) # eg: 115653

     # *** Gene info:
     for entrezgene_gene in entrezgene.findall('Entrezgene_gene'):
       for gene_ref in entrezgene_gene.findall('Gene-ref'):
         for gene_ref_locus in gene_ref.findall('Gene-ref_locus'):   # A2M
           print("Locus:",gene_ref_locus.text)
         for gene_ref_desc in gene_ref.findall('Gene-ref_desc'):    # alpha-2-macroglobulin
           print("Desc:",gene_ref_desc.text)
         for gene_ref_maploc in gene_ref.findall('Gene-ref_maploc'):  # 12p13.31
           print("Maploc:",gene_ref_maploc.text)
         for gene_ref_db in gene_ref.findall('Gene-ref_db'):
           for dbtag in gene_ref_db.findall('Dbtag'):   #(repeats for HGNC, Ensembl, HPRD, MIM, Vega)
             for dbtag_db in dbtag.findall('Dbtag_db'):  # HGNC
               dbtag_db_text = dbtag_db.text
             for dbtag_tag in dbtag.findall('Dbtag_tag'):
               for object_id in dbtag_tag.findall('Object-id'):
                 for object_id_str in object_id.findall('Object-id_str'):  # HGNC:7  (ENSG00000175899, 00072, 103950, OTTHUMG00000150267)
                   print(dbtag_db_text+":",object_id_str.text)
                   
         synonyms = ''
         for gene_ref_syn in gene_ref.findall('Gene-ref_syn'):
           for gene_ref_syn_E in gene_ref_syn.findall('Gene-ref_syn_E'): # A2MD CPAMD5  FWP007  S863-7 (repeats for each synonym)
             # print("Gene-ref synonym:",gene_ref_syn_E.text)
             if synonyms == '': synonyms = gene_ref_syn_E.text
             else: synonyms += ' | '+gene_ref_syn_E.text
         if synonyms != '': print("Synonyms:",synonyms)
         
       for entrezgene_summary in entrezgene.findall('Entrezgene_summary'): # Some genes don't have a summary
         print("Gene summary:",entrezgene_summary.text)
         
         
       for entrezgene_comments in entrezgene.findall('Entrezgene_comments'):
#    .....
         for gene_commentary in entrezgene_comments.findall('Gene-commentary'):
#           print("gene_commentary:",gene_commentary)
#           for gene_commentary_heading in gene_commentary.findall('Gene-commentary_heading'):
#             print("Gene_commentary_heading:",gene_commentary_heading.text)

#      <Gene-commentary_type value="comment">254</Gene-commentary_type>
#      <Gene-commentary_heading>NCBI Reference Sequences (RefSeq)</Gene-commentary_heading>
           for gene_commentary_comment in gene_commentary.findall('Gene-commentary_comment'):
             for gene_commentary2 in gene_commentary_comment.findall('Gene-commentary'):
#               print("gene_commentary2:",gene_commentary2)
#               for gene_commentary_heading in gene_commentary2.findall('Gene-commentary_heading'):
#                 print("Gene_commentary2_heading:",gene_commentary_heading.text)
               
#          <Gene-commentary_type value="comment">254</Gene-commentary_type>
#          <Gene-commentary_heading>RefSeqs maintained independently of Annotated Genomes</Gene-commentary_heading>
               for gene_commentary_products in gene_commentary2.findall('Gene-commentary_products'):
                 print("*****gene_commentary_products:",gene_commentary_products)
                 for gene_commentary3 in gene_commentary_products.findall('Gene-commentary'):
                   print("gene_commentary3:",gene_commentary3)
                   for gene_commentary_heading in gene_commentary3.findall('Gene-commentary_heading'):
                     print("Gene_commentary3_heading:",gene_commentary_heading.text)
                   
#              <Gene-commentary_type value="mRNA">3</Gene-commentary_type>
#              <Gene-commentary_heading>mRNA Sequence</Gene-commentary_heading>
#              <Gene-commentary_accession>NM_005160</Gene-commentary_accession>
#              <Gene-commentary_version>3</Gene-commentary_version>
#              .....
                   for gene_commentary_products2 in gene_commentary3.findall('Gene-commentary_products'):
                     for gene_commentary4 in gene_commentary_products2.findall('Gene-commentary'):
                       print("gene_commentary4:",gene_commentary4)                       
                       for gene_commentary_type in gene_commentary4.findall('Gene-commentary_type'):
                         print("Gene_commentary4_type:",gene_commentary_type.attrib['value'])
                       for gene_commentary_accession in gene_commentary4.findall('Gene-commentary_accession'):
                         print("Gene_commentary4_accession:",gene_commentary_accession.text)
                       for gene_commentary_heading in gene_commentary4.findall('Gene-commentary_heading'):                       
                         print("Gene_commentary4_heading:",gene_commentary_heading.text)

#                  <Gene-commentary_type value="peptide">8</Gene-commentary_type>
#                  <Gene-commentary_heading>Product</Gene-commentary_heading>
#                  <Gene-commentary_accession>NP_005151</Gene-commentary_accession>
#                  <Gene-commentary_version>2</Gene-commentary_version>
#                  'Gene-commentary_source'):
#                    'Other-source'):
#                      'Other-source_src'):
#                        'Dbtag')
#                          'Dbtag_db'):  Protein</Dbtag_db>
#                          'Dbtag_tag'):
#                            'Object-id'):
#                              'Object-id_id'): 148539879
#                            </Object-id>
#                          </Dbtag_tag>
#                        </Dbtag>
#                      </Other-source_src>
#                      <Other-source_anchor>NP_005151</Other-source_anchor>
#                      <Other-source_post-text>beta-adrenergic receptor kinase 2</Other-source_post-text>
#                    </Other-source>
#                  </Gene-commentary_source>
#                  <Gene-commentary_seqs>
#                    <Seq-loc>
#                      <Seq-loc_whole>
#                        <Seq-id>
#                          <Seq-id_gi>148539879</Seq-id_gi>
#                        </Seq-id>
#                      </Seq-loc_whole>
#                    </Seq-loc>
#                  </Gene-commentary_seqs>
                  
#                  'Gene-commentary_comment'):
#                    ...
#                    'Gene-commentary'):
#                      <Gene-commentary_type value="other">255</Gene-commentary_type>
#                      <Gene-commentary_heading>Related</Gene-commentary_heading>
                       for gene_commentary_source in gene_commentary4.findall('Gene-commentary_source'):
                         print("gene_commentary_source:",gene_commentary_source)
                         for other_source in gene_commentary_source.findall('Other-source'):
                           for other_source_src in other_source.findall('Other-source_src'):
                             for dbtag in other_source_src.findall('Dbtag'):
                               for dbtag_db in dbtag.findall('Dbtag_db'):   # Ensembl
                                 print("Dbtag_db:",dbtag_db.text)
                               for dbtag_tag in dbtag.findall('Dbtag_tag'):
                                 print("* Dbtag_tag",dbtag_tag)
                                 for object_id in dbtag_tag.findall('Object-id'):
                                   print("** Object_id:",object_id)
                                   for object_id_str in object_id.findall('Object-id_str'):  # ENSP00000317578
                                     print("*** Object-id_str:",object_id_str.text)
                                   for object_id_id in object_id.findall('Object-id_id'):  # ENSP00000317578
                                     print("*** Object-id_id:",object_id_id.text)
                    
#                    'Gene-commentary'):
#                      <Gene-commentary_type value="other">255</Gene-commentary_type>
#                      <Gene-commentary_heading>UniProtKB</Gene-commentary_heading>
#                      <Gene-commentary_source></Gene-commentary_source>
#                      <Gene-commentary_comment>
#                        <Gene-commentary>
#                          <Gene-commentary_type value="other">255</Gene-commentary_type>
#                          <Gene-commentary_source>
#                            <Other-source>
#                              <Other-source_src>
#                                <Dbtag>
#                                  <Dbtag_db>UniProtKB/TrEMBL</Dbtag_db>
#                                  <Dbtag_tag>
#                                    <Object-id>
#                                      <Object-id_str>A0A024R1D8</Object-id_str>
#                                    </Object-id>
#                                  </Dbtag_tag>
#                                </Dbtag>
#                              </Other-source_src>
#                              <Other-source_anchor>A0A024R1D8</Other-source_anchor>
#                            </Other-source>
#                            <Other-source>
#                              <Other-source_src>
#                                <Dbtag>
#                                  <Dbtag_db>UniProtKB/Swiss-Prot</Dbtag_db>
#                                  <Dbtag_tag>
#                                    <Object-id>
#                                      <Object-id_str>P35626</Object-id_str>    
#
#=====         
         
         
     print("#END\n")
"""                                                              
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

"""
Entrezgene-Set
  Entrezgene  (repeats for each gene requested)
  
    Entrezgene_track-info
      Gene-track
        Gene-track_geneid  2

*** Only if GeneId has changed:
    Gene-track_current-id
      Dbtag
        Dbtag_db  LocusID
        Dbtag_tag
          Object-id
            Object-id_id  115653
      Dbtag
        Dbtag_db  GeneID
        Dbtag_tag
          Object-id
            Object-id_id  115653


*** Gene info:
    Entrezgene_gene
      Gene-ref
        Gene-ref_locus   A2M
        Gene-ref_desc    alpha-2-macroglobulin
        Gene-ref_maploc  12p13.31
        
        Gene-ref_db
           Dbtag   (repeats for HGNC, Ensembl, HPRD, MIM, Vega)
            Dbtag_db   HGNC
            Dbtag_tag
               Object-id
                  Object-id_str   HGNC:7  (ENSG00000175899, 00072, 103950, OTTHUMG00000150267)
            </Dbtag_tag>
          </Dbtag>
          
        Gene-ref_syn
          Gene-ref_syn_E A2MD  (repeats for each synonym)
          Gene-ref_syn_E CPAMD5
          Gene-ref_syn_E FWP007
          Gene-ref_syn_E S863-7
        </Gene-ref_syn>
      </Gene-ref>

    Entrezgene_summary
      Alpha-2-macroglobulin is a protease inhibitor and cytokine transporter. It inhibits many proteases, including trypsin, thrombin and collagenase. A2M is implicated in Alzheimer disease (AD) due to its ability to mediate the clearance and degradation of A-beta, the major component of beta-amyloid deposits. [provided by RefSeq, Jul 2008]
    </Entrezgene_summary>
"""
          
"""
========================================
# http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&id=2&retmode=xml

<Entrezgene-Set>
  <Entrezgene>
    <Entrezgene_track-info>...</Entrezgene_track-info>
    <Entrezgene_type value="protein-coding">6</Entrezgene_type>
    <Entrezgene_source>...</Entrezgene_source>
    <Entrezgene_gene>
      <Gene-ref>
        <Gene-ref_locus>A2M</Gene-ref_locus>
        <Gene-ref_desc>alpha-2-macroglobulin</Gene-ref_desc>
        <Gene-ref_maploc>12p13.31</Gene-ref_maploc>
        <Gene-ref_db>
          <Dbtag>
            <Dbtag_db>HGNC</Dbtag_db>
            <Dbtag_tag>
               <Object-id>
                  <Object-id_str>HGNC:7</Object-id_str>
               </Object-id>
            </Dbtag_tag>
          </Dbtag>
          <Dbtag>
            <Dbtag_db>Ensembl</Dbtag_db>
            <Dbtag_tag>
               <Object-id>
                  <Object-id_str>ENSG00000175899</Object-id_str>
               </Object-id>
            </Dbtag_tag>
          </Dbtag>
          <Dbtag>
            <Dbtag_db>HPRD</Dbtag_db>
            <Dbtag_tag>
               <Object-id>
                  <Object-id_str>00072</Object-id_str>
               </Object-id>
            </Dbtag_tag>
          </Dbtag>
          <Dbtag>
            <Dbtag_db>MIM</Dbtag_db>
            <Dbtag_tag>
               <Object-id>
                 <Object-id_id>103950</Object-id_id>
               </Object-id>
            </Dbtag_tag>
          </Dbtag>
          <Dbtag>
            <Dbtag_db>Vega</Dbtag_db>
            <Dbtag_tag>
               <Object-id>
                 <Object-id_str>OTTHUMG00000150267</Object-id_str>
               </Object-id>
            </Dbtag_tag>
          </Dbtag>
        </Gene-ref_db>
        <Gene-ref_syn>
          <Gene-ref_syn_E>A2MD</Gene-ref_syn_E>
          <Gene-ref_syn_E>CPAMD5</Gene-ref_syn_E>
          <Gene-ref_syn_E>FWP007</Gene-ref_syn_E>
          <Gene-ref_syn_E>S863-7</Gene-ref_syn_E>
        </Gene-ref_syn>
      </Gene-ref>
    </Entrezgene_gene>
    <Entrezgene_prot>
      <Prot-ref>
        <Prot-ref_name>
          <Prot-ref_name_E>
             C3 and PZP-like alpha-2-macroglobulin domain-containing protein 5
          </Prot-ref_name_E>
          <Prot-ref_name_E>alpha-2-M</Prot-ref_name_E>
        </Prot-ref_name>
        <Prot-ref_desc>alpha-2-macroglobulin</Prot-ref_desc>
        </Prot-ref>
    </Entrezgene_prot>
    <Entrezgene_summary>
      Alpha-2-macroglobulin is a protease inhibitor and cytokine transporter. It inhibits many proteases, including trypsin, thrombin and collagenase. A2M is implicated in Alzheimer disease (AD) due to its ability to mediate the clearance and degradation of A-beta, the major component of beta-amyloid deposits. [provided by RefSeq, Jul 2008]
    </Entrezgene_summary>
    <Entrezgene_location>
      <Maps>
        <Maps_display-str>12p13.31</Maps_display-str>
        <Maps_method>
          <Maps_method_map-type value="cyto"/>
        </Maps_method>
      </Maps>
    </Entrezgene_location>
    
<Entrezgene_properties>
<Gene-commentary>
<Gene-commentary_comment>
<Gene-commentary>    
***    Also Ensembl protein id (maybe useful for StringDB
    <Gene-commentary_source>
<Other-source>
<Other-source_src>
<Dbtag>
<Dbtag_db>Ensembl</Dbtag_db>
<Dbtag_tag>
<Object-id>
<Object-id_str>ENSP00000323929</Object-id_str>
</Object-id>
</Dbtag_tag>
</Dbtag>
    
  <Entrezgene_comments>
    .....
    <Gene-commentary>
      <Gene-commentary_type value="comment">254</Gene-commentary_type>
      <Gene-commentary_heading>NCBI Reference Sequences (RefSeq)</Gene-commentary_heading>
      <Gene-commentary_comment>
        <Gene-commentary>
          <Gene-commentary_type value="comment">254</Gene-commentary_type>
          <Gene-commentary_heading>RefSeqs maintained independently of Annotated Genomes</Gene-commentary_heading>
          <Gene-commentary_products>
            <Gene-commentary>
              <Gene-commentary_type value="mRNA">3</Gene-commentary_type>
              <Gene-commentary_heading>mRNA Sequence</Gene-commentary_heading>
              <Gene-commentary_accession>NM_005160</Gene-commentary_accession>
              <Gene-commentary_version>3</Gene-commentary_version>
              .....
              <Gene-commentary_products>
                <Gene-commentary>
                  <Gene-commentary_type value="peptide">8</Gene-commentary_type>
                  <Gene-commentary_heading>Product</Gene-commentary_heading>
                  <Gene-commentary_accession>NP_005151</Gene-commentary_accession>
                  <Gene-commentary_version>2</Gene-commentary_version>
                  <Gene-commentary_source>
                    <Other-source>
                      <Other-source_src>
                        <Dbtag>
                          <Dbtag_db>Protein</Dbtag_db>
                          <Dbtag_tag>
                            <Object-id>
                              <Object-id_id>148539879</Object-id_id>
                            </Object-id>
                          </Dbtag_tag>
                        </Dbtag>
                      </Other-source_src>
                      <Other-source_anchor>NP_005151</Other-source_anchor>
                      <Other-source_post-text>beta-adrenergic receptor kinase 2</Other-source_post-text>
                    </Other-source>
                  </Gene-commentary_source>
                  <Gene-commentary_seqs>
                    <Seq-loc>
                      <Seq-loc_whole>
                        <Seq-id>
                          <Seq-id_gi>148539879</Seq-id_gi>
                        </Seq-id>
                      </Seq-loc_whole>
                    </Seq-loc>
                  </Gene-commentary_seqs>
                  <Gene-commentary_comment>    
                    ...
                    <Gene-commentary>
                      <Gene-commentary_type value="other">255</Gene-commentary_type>
                      <Gene-commentary_heading>Related</Gene-commentary_heading>
                      <Gene-commentary_source>
                        <Other-source>
                          <Other-source_src>
                            <Dbtag>
                              <Dbtag_db>Ensembl</Dbtag_db>
                              <Dbtag_tag>
                                <Object-id>
                                  <Object-id_str>ENSP00000317578</Object-id_str>
                                </Object-id>
                              </Dbtag_tag>
                            </Dbtag>
                          </Other-source_src>
                        </Other-source>
                      </Gene-commentary_source>
                    </Gene-commentary>
                    <Gene-commentary>
                      <Gene-commentary_type value="other">255</Gene-commentary_type>
                      <Gene-commentary_heading>UniProtKB</Gene-commentary_heading>
                      <Gene-commentary_source></Gene-commentary_source>
                      <Gene-commentary_comment>
                        <Gene-commentary>
                          <Gene-commentary_type value="other">255</Gene-commentary_type>
                          <Gene-commentary_source>
                            <Other-source>
                              <Other-source_src>
                                <Dbtag>
                                  <Dbtag_db>UniProtKB/TrEMBL</Dbtag_db>
                                  <Dbtag_tag>
                                    <Object-id>
                                      <Object-id_str>A0A024R1D8</Object-id_str>
                                    </Object-id>
                                  </Dbtag_tag>
                                </Dbtag>
                              </Other-source_src>
                              <Other-source_anchor>A0A024R1D8</Other-source_anchor>
                            </Other-source>
                            <Other-source>
                              <Other-source_src>
                                <Dbtag>
                                  <Dbtag_db>UniProtKB/Swiss-Prot</Dbtag_db>
                                  <Dbtag_tag>
                                    <Object-id>
                                      <Object-id_str>P35626</Object-id_str>    
    
=========================================
If Entrez Gene id changed, then: 
<Entrezgene-Set>
  <Entrezgene>
  <Entrezgene_track-info>
<Gene-track>
<Gene-track_geneid>100133046</Gene-track_geneid>
<Gene-track_status value="secondary">1</Gene-track_status>
<Gene-track_current-id>
<Dbtag>
<Dbtag_db>LocusID</Dbtag_db>
<Dbtag_tag>
<Object-id>
<Object-id_id>115653</Object-id_id>
</Object-id>
</Dbtag_tag>
</Dbtag>
<Dbtag>
<Dbtag_db>GeneID</Dbtag_db>
<Dbtag_tag>
<Object-id>
<Object-id_id>115653</Object-id_id>
</Object-id>
</Dbtag_tag>
</Dbtag>

=====
"""



def process_all_genes_in_db():
 BATCH_SIZE=2000 # number of ids to submit in one query.
 genes_without_entrez_ids = []
 genes_without_summary = []
 entrez_to_genename_dict = dict()

 genes_processed = 0
 total_gene_summaries_found_count = 0

 fout1 = open( "entrez_gene_summaries.xml","w")
 fout2 = open("entrez_gene_summaries.txt","w")
 fout2.write("Gene_name\tEntrez_id\tSummary\n")

 with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
  for g in Gene.objects.all().iterator():
    #print(g.gene_name, g.entrez_id)
    if g.entrez_id=='' or g.entrez_id=='NoEntrezId':
        genes_without_entrez_ids.append(g.gene_name)
    else:    
        entrez_to_genename_dict[g.entrez_id] = g.gene_name
        
    #driver_text = '*DRIVER*' if g.is_driver else ''
    genes_processed += 1
    
    # Request 100 interactions at a time, to reduce load on server
    if len(entrez_to_genename_dict) == BATCH_SIZE:
      total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

#      unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
           # print("GENE:\t%s\t%s" %(gene_name,entrez_summaries[entrez_id]))

#           genes_with_summary_count += 1
#        else:
#           genes_without_summary.append(gene_name)        
      entrez_to_genename_dict.clear()
        
      #print("genes_processed:", genes_processed)
      
  if len(entrez_to_genename_dict) > 0: # Process any remaining genes as < BATCH_SIZE
    total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

 fout1.close()
 fout2.close()
    
 print("Genes_processed: %d,  Gene_summaries_found: %d" %(genes_processed, total_gene_summaries_found_count))
 print("\nGenes_without_entrez_ids: %d:" %(len(genes_without_entrez_ids)) )
 print("\n".join(genes_without_entrez_ids))

      #gene_count = 0



def process_all_genes_in_file():
 BATCH_SIZE=2000 # number of ids to submit in one query.
 genes_without_entrez_ids = []
 genes_without_summary = []
 entrez_to_genename_dict = dict()

 genes_processed = 0
 total_gene_summaries_found_count = 0

 fout1 = open( "entrez_gene_summaries.xml","w")
 fout2 = open("entrez_gene_summaries.txt","w")
 fout2.write("Gene_name\tEntrez_id\tSummary\n")

 with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
  for g in Gene.objects.all().iterator():
    #print(g.gene_name, g.entrez_id)
    if g.entrez_id=='' or g.entrez_id=='NoEntrezId':
        genes_without_entrez_ids.append(g.gene_name)
    else:    
        entrez_to_genename_dict[g.entrez_id] = g.gene_name
        
    #driver_text = '*DRIVER*' if g.is_driver else ''
    genes_processed += 1
    
    # Request 100 interactions at a time, to reduce load on server
    if len(entrez_to_genename_dict) == BATCH_SIZE:
      total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

#      unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
           # print("GENE:\t%s\t%s" %(gene_name,entrez_summaries[entrez_id]))

#           genes_with_summary_count += 1
#        else:
#           genes_without_summary.append(gene_name)        
      entrez_to_genename_dict.clear()
        
      #print("genes_processed:", genes_processed)
      
  if len(entrez_to_genename_dict) > 0: # Process any remaining genes as < BATCH_SIZE
    total_gene_summaries_found_count += get_entrez_summaries(entrez_to_genename_dict, fout1,fout2)

 fout1.close()
 fout2.close()
    
 print("Genes_processed: %d,  Gene_summaries_found: %d" %(genes_processed, total_gene_summaries_found_count))
 print("\nGenes_without_entrez_ids: %d:" %(len(genes_without_entrez_ids)) )
 print("\n".join(genes_without_entrez_ids))

      #gene_count = 0

if __name__ == "__main__":
    # process_all_genes_in_db()
    
    fout1 = open( "entrez_gene_full_details.xml","w")
    fout2 = open("entrez_gene_full_details.txt","w")
    fout2.write("Gene_name\tEntrez_id\tSummary\n")
    entrez_to_genename_dict=dict()
    get_entrez_full(entrez_to_genename_dict, fout1, fout2)
    
    #get_entrez_summaries({'2064':'ERBB2', '7422':'VEGFA'},None,None)
    
    #test_post()
