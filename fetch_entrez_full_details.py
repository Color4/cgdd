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


def warn(message):
	sys.stderr.write('* WARNING:  %s\n' % message)
	

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






"""
Why are genes 40,43 and 440163 duplicated (I manually removed these from output file: entrez_gene_full_details_Achilles_and_Colt.txt)

row:         ['40', 'live', '0', '', '', 'ASIC2', '17q12', 'HGNC:99', 'ENSG00000108684', '03471', '601784', 'OTTHUMG00000132885', 'ENSP00000225823', 'Q16515', 'acid sensing ion channel subunit 2', 'ACCN | BNC1 | MDEG | ACCN1 | BNaC1 | ASIC2a | hBNaC1', 'This gene encodes a member of the degenerin/epithelial sodium channel (DEG/ENaC) superfamily. The members of this family are amiloride-sensitive sodium channels that contain intracellular N and C termini, 2 hydrophobic transmembrane regions, and a large extracellular loop, which has many cysteine residues with conserved spacing. The member encoded by this gene may play a role in neurotransmission. In addition, a heteromeric association between this member and acid-sensing (proton-gated) ion channel 3 has been observed to co-assemble into proton-gated channels sensitive to gadolinium. Alternative splicing has been observed at this locus and two variants, encoding distinct isoforms, have been identified. [provided by RefSeq, Feb 2012]']
entrez_info: ['40', 'live', '0', '', '', 'ASIC2', '17q12', 'HGNC:99', 'ENSG00000108684', '03471', '601784', 'OTTHUMG00000132885', 'ENSP00000225823', 'Q16515', 'acid sensing ion channel subunit 2', 'ACCN | BNC1 | MDEG | ACCN1 | BNaC1 | ASIC2a | hBNaC1', 'This gene encodes a member of the degenerin/epithelial sodium channel (DEG/ENaC) superfamily. The members of this family are amiloride-sensitive sodium channels that contain intracellular N and C termini, 2 hydrophobic transmembrane regions, and a large extracellular loop, which has many cysteine residues with conserved spacing. The member encoded by this gene may play a role in neurotransmission. In addition, a heteromeric association between this member and acid-sensing (proton-gated) ion channel 3 has been observed to co-assemble into proton-gated channels sensitive to gadolinium. Alternative splicing has been observed at this locus and two variants, encoding distinct isoforms, have been identified. [provided by RefSeq, Feb 2012]']

row:         ['43', 'live', '0', '', '', 'ACHE', '7q22', 'HGNC:108', 'ENSG00000087085', '00010', '100740', 'OTTHUMG00000157033', 'ENSP00000303211', 'P22303', 'acetylcholinesterase (Cartwright blood group)', 'YT | ACEE | ARACHE | N-ACHE', 'Acetylcholinesterase hydrolyzes the neurotransmitter, acetylcholine at neuromuscular junctions and brain cholinergic synapses, and thus terminates signal transmission. It is also found on the red blood cell membranes, where it constitutes the Yt blood group antigen. Acetylcholinesterase exists in multiple molecular forms which possess similar catalytic properties, but differ in their oligomeric assembly and mode of cell attachment to the cell surface. It is encoded by the single ACHE gene, and the structural diversity in the gene products arises from alternative mRNA splicing, and post-translational associations of catalytic and structural subunits. The major form of acetylcholinesterase found in brain, muscle and other tissues is the hydrophilic species, which forms disulfide-linked oligomers with collagenous, or lipid-containing structural subunits. The other, alternatively spliced form, expressed primarily in the erythroid tissues, differs at the C-terminal end, and contains a cleavable hydrophobic peptide with a GPI-anchor site. It associates with the membranes through the phosphoinositide (PI) moieties added post-translationally. [provided by RefSeq, Jul 2008]']
entrez_info: ['43', 'live', '0', '', '', 'ACHE', '7q22', 'HGNC:108', 'ENSG00000087085', '00010', '100740', 'OTTHUMG00000157033', 'ENSP00000303211', 'P22303', 'acetylcholinesterase (Cartwright blood group)', 'YT | ACEE | ARACHE | N-ACHE', 'Acetylcholinesterase hydrolyzes the neurotransmitter, acetylcholine at neuromuscular junctions and brain cholinergic synapses, and thus terminates signal transmission. It is also found on the red blood cell membranes, where it constitutes the Yt blood group antigen. Acetylcholinesterase exists in multiple molecular forms which possess similar catalytic properties, but differ in their oligomeric assembly and mode of cell attachment to the cell surface. It is encoded by the single ACHE gene, and the structural diversity in the gene products arises from alternative mRNA splicing, and post-translational associations of catalytic and structural subunits. The major form of acetylcholinesterase found in brain, muscle and other tissues is the hydrophilic species, which forms disulfide-linked oligomers with collagenous, or lipid-containing structural subunits. The other, alternatively spliced form, expressed primarily in the erythroid tissues, differs at the C-terminal end, and contains a cleavable hydrophobic peptide with a GPI-anchor site. It associates with the membranes through the phosphoinositide (PI) moieties added post-translationally. [provided by RefSeq, Jul 2008]']

row:         ['440163', 'live', '0', '', '', 'RNASE13', '14q11.1', 'HGNC:25285', 'ENSG00000206150', '17980', '', 'OTTHUMG00000171110', 'ENSP00000372410', 'Q5GAN3', 'ribonuclease A family member 13 (inactive)', 'RAL1 | HEL-S-86p', '']
entrez_info: ['440163', 'live', '0', '', '', 'RNASE13', '14q11.1', 'HGNC:25285', 'ENSG00000206150', '17980', '', 'OTTHUMG00000171110', 'ENSP00000372410', 'Q5GAN3', 'ribonuclease A family member 13 (inactive)', 'RAL1 | HEL-S-86p', '']

# Also what should we do with secondary ids:
* WARNING:  gene_track_entrez_id 441528 != current_entrez_id 389906, status:secondary
* WARNING:  gene_track_entrez_id 9503 != current_entrez_id 653067, status:secondary
* WARNING:  gene_track_entrez_id 221016 != current_entrez_id 79741, status:secondary
* WARNING:  gene_track_entrez_id 164022 != current_entrez_id 653505, status:secondary
* WARNING:  gene_track_entrez_id 164022 != current_entrez_id 653505, status:secondary
* WARNING:  gene_track_entrez_id 400863 != current_entrez_id 100506334, status:secondary
* WARNING:  gene_track_entrez_id 728461 != current_entrez_id 102723547, status:secondary

"""


def get_entrez_full(entrez_to_genename_dict, is_first, fout1, fout2):

    # Minimizing the Number of Requests: If a task requires searching for and/or downloading a large number of records, it is much more efficient to use the Entrez History to upload and/or retrieve these records in batches rather than using separate requests for each record. Please refer to Application 3 in Chapter 3 for an example. Many thousands of IDs can be uploaded using a single EPost request, and several hundred records can be downloaded using one EFetch request.   http://www.ncbi.nlm.nih.gov/books/NBK25497/
    # First use ESearch to retrieve the GI numbers for these sequences and post them on the History server, then use multiple EFetch calls to retrieve the data in batches of 500.
    
    # see: http://www.ncbi.nlm.nih.gov/books/NBK25498/#chapter3.Application_4_Finding_unique_se
    
    # eg: $url = $base . "epost.fcgi?db=$db&id=$id_list";   

   if is_first:  # write_header
     fout2.write("Entrez"
         "\tStatus"
         "\tStatus_int"
         "\tCurrent_entrez"
         "\tCurrent_locus"
         "\tGene_name"
         "\tMaploc"
         "\tHGNC"
         "\tEnsembl_gene"
         "\tHPRD"
         "\tOMIM"
         "\tVEGA"
         "\tEnsembl_protein"
         "\tUniProt" 
         "\tDesc"                 
         "\tSynonyms"
         "\tSummary"
         "\n"
         )



   url = EUTILS_URL+"efetch.fcgi?db=gene" # Instead of "esummary.fcgi?db=gene"
   data = {'retmode':'xml', 'id': ",".join(entrez_to_genename_dict.keys())}  # Need to specify retmode of xml, otherwise returns asn.1, default
   headers = {"Content-Type": "application/x-www-form-urlencoded"}
   
   r = requests.post(url, headers=headers, data=data) # insead of:  r = requests.get(url) 
      
   r.raise_for_status()  # print(r.status_code == requests.codes.ok)
   #print(r.encoding)
   #print(r.headers)
   gene_summaries_found_count = 0
   
   fout1.write(r.text)
   fout1.write("\n#END\n")

   root = ET.fromstring(r.text) # root is 'Entrezgene-Set'
   # OR to read from file:
   #tree = ET.parse('test_entrez_full.xml'); root=tree.getroot()
   #tree = ET.parse('test_entrez_full2.xml'); root=tree.getroot()
   #tree = ET.parse('test_entrez_full_ERBB2.xml'); root=tree.getroot()   
   
   # Removed these two lines:
   # <?xml version="1.0" ?>
   # <!DOCTYPE Entrezgene-Set PUBLIC "-//NLM//DTD NCBI-Entrezgene, 21st January 2005//EN" "http://www.ncbi.nlm.nih.gov/data_specs/dtd/NCBI_Entrezgene.dtd">

     # print(entrezgene.tag, entrezgene.attrib, entrezgene.text)
#     if entrezgene.attrib['status'] != "OK":
#        print("ERROR: DocSum status: ",docsumset.attrib['status'])

   PRINT_HEADINGS = False
   PRINT_TYPE = False
   PRINT_VALUE = False


   if PRINT_VALUE: print("#START")
      
#   for entrezgene in root.findall('Entrezgene-Set'):  # The set of gene(s) requested
   for entrezgene in root.findall('Entrezgene'):  # repeats for each gene requested
     gene_track_entrez_id = '' # eg: 157
     gene_track_status_string = ''  # eg: 'live'
     gene_track_status_int =  ''    # eg: 0 for 'live' 
     current_entrez_id = ''
     current_locus = ''  # current gene_name ?
     gene_name = '' # Locus eg. GRK3
     desc = '' # eg: G protein-coupled receptor kinase 3
     maploc = '' # eg: 22q12.1
     hgnc = '' # eg: HGNC:290
     ensembl_gene = ''  # eg: ENSG00000100077
     hprd = '' # eg: 00183
     omim = '' # eg: 109636
     vega = '' # eg: OTTHUMG00000150280
     synonyms = '' # BARK2 | ADRBK2
     summary = ''  #  The beta-adrenergic receptor kinase specifically phosphorylates the agonist-occupied form of the beta-adrenergic and related G protein-coupled receptors. Overall, the beta adrenergic receptor kinase 2 has 85% amino acid similarity with beta adrenergic receptor kinase 1, with the protein kinase catalytic domain having 95% similarity. These data suggest the existence of a family of receptor kinases which may serve broadly to regulate receptor function. [provided by RefSeq, Jul 2008]
     ensembl_protein = '' # eg:  ENSP00000317578
     uniprot = '' # eg: P35626   

     for entrezgene_track_info in entrezgene.findall('Entrezgene_track-info'):
       for gene_track in entrezgene_track_info.findall('Gene-track'):
         for gene_track_geneid in gene_track.findall('Gene-track_geneid'):
           gene_track_entrez_id = gene_track_geneid.text # ie. the requested entrez_id
           if PRINT_VALUE: print("Gene track entrez_id:",gene_track_entrez_id)
                                 
         for gene_track_status in gene_track.findall('Gene-track_status'):
           gene_track_status_string = gene_track_status.attrib['value'] # != live 0, or secondary 1
           if gene_track_status_string == 'discontinued': warn("For '%s' '%s': DISCONTINUED Gene_track_status: '%s'" %(gene_track_entrez_id,gene_name,gene_track_status_string))
           if gene_track_status_string not in ('live', 'secondary'): warn("For '%s' '%s': Unexpected gene_track_status: '%s'" %(gene_track_entrez_id,gene_name,gene_track_status_string))
           
           gene_track_status_int = gene_track_status.text  # 0 or 1, etc
           
           if PRINT_VALUE: print("Gene track_status value: '%s',  gene_track_status_text: '%s'" %(gene_track_status_string,gene_track_status_int) )
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
                    if PRINT_VALUE: print(dbtag_db_text+":",object_id_id.text) # eg: 115653
                    if dbtag_db_text == 'LocusID': current_locus = object_id_id.text
                    elif dbtag_db_text == 'GeneID': current_entrez_id = object_id_id.text
                    else: warn("Unexpected Current: %s %s" %(dbtag_db_text, object_id_id.text))
                    # Could this sometimes be a object_id_str rather than object_id_id
           if current_locus != current_entrez_id: warn("Expected current_locus:%s != current_entrez_id:%s" %(current_locus,current_entrez_id))
           
     # *** Gene info:
     for entrezgene_gene in entrezgene.findall('Entrezgene_gene'):
       for gene_ref in entrezgene_gene.findall('Gene-ref'):
         for gene_ref_locus in gene_ref.findall('Gene-ref_locus'):   # A2M
           if PRINT_VALUE: print("Locus:",gene_ref_locus.text)
           gene_name = gene_ref_locus.text
         for gene_ref_desc in gene_ref.findall('Gene-ref_desc'):    # alpha-2-macroglobulin
           if PRINT_VALUE: print("Desc:",gene_ref_desc.text)
           desc = gene_ref_desc.text
         for gene_ref_maploc in gene_ref.findall('Gene-ref_maploc'):  # 12p13.31
           if PRINT_VALUE: print("Maploc:",gene_ref_maploc.text)
           maploc = gene_ref_maploc.text
         for gene_ref_db in gene_ref.findall('Gene-ref_db'):
           for dbtag in gene_ref_db.findall('Dbtag'):   #(repeats for HGNC, Ensembl, HPRD, MIM, Vega)
             for dbtag_db in dbtag.findall('Dbtag_db'):  # HGNC
               dbtag_db_text = dbtag_db.text
             for dbtag_tag in dbtag.findall('Dbtag_tag'):
               for object_id in dbtag_tag.findall('Object-id'):
                 for object_id_str in object_id.findall('Object-id_str'):  # HGNC:7  (ENSG00000175899, 00072, OTTHUMG00000150267) as are strings
                   if PRINT_VALUE: print(dbtag_db_text+":",object_id_str.text)
                   if   dbtag_db_text == 'HGNC':    hgnc = object_id_str.text  # eg: HGNC:290
                   elif dbtag_db_text == 'Ensembl': ensembl_gene = object_id_str.text
                   elif dbtag_db_text == 'HPRD':    hprd = object_id_str.text
                   elif dbtag_db_text == 'Vega':    vega = object_id_str.text
                   else: warn("For %s $%s: Unexpected Gene-ref DB str: %s %s" %(gene_track_entrez_id,gene_name,dbtag_db_text, object_id_str.text))
                   
                 for object_id_id in object_id.findall('Object-id_id'):  # MIM  (103950) as is an integer
                   if PRINT_VALUE: print(dbtag_db_text+":",object_id_id.text)
                   if dbtag_db_text == 'MIM': omim = object_id_id.text
                   else: warn("Unexpected Gene-ref DB id: %s %s" %(dbtag_db_text, object_id_id.text))
                   
         for gene_ref_syn in gene_ref.findall('Gene-ref_syn'):
           for gene_ref_syn_E in gene_ref_syn.findall('Gene-ref_syn_E'): # A2MD CPAMD5  FWP007  S863-7 (repeats for each synonym)
             # if PRINT_VALUE: print("Gene-ref synonym:",gene_ref_syn_E.text)
             if synonyms == '': synonyms = gene_ref_syn_E.text
             else: synonyms += ' | '+gene_ref_syn_E.text
         if PRINT_VALUE: print("Synonyms:",synonyms)
         
       for entrezgene_summary in entrezgene.findall('Entrezgene_summary'): # Some genes don't have a summary
         if PRINT_VALUE: print("Gene summary:",entrezgene_summary.text)
         summary = entrezgene_summary.text



# Better would be to use the XPath args, eg::
#>>> for elem in tree.iterfind('branch/sub-branch'):
#...   print elem.tag, elem.attrib
#...
#sub-branch {'name': 'subrelease01'}
#It found all the elements in the tree tagged sub-branch that are below an element called branch. And here's how to find all branch elements with a specific name attribute:
#
#>>> for elem in tree.iterfind('branch[@name="release01"]'):  # ie. attrib is name = value
#...   print elem.tag, elem.attrib
#...
#branch {'hash': 'f200013e', 'name': 'release01'}

       for entrezgene_comments in entrezgene.findall('Entrezgene_comments'):
#    .....
         for gene_commentary1 in entrezgene_comments.findall('Gene-commentary'):
#           print("gene_commentary1:",gene_commentary1)
           for gene_commentary_heading in gene_commentary1.findall('Gene-commentary_heading'):
             gene_commentary_heading_text = gene_commentary_heading.text
             if PRINT_HEADINGS:             
               print("Gene_commentary1_heading:",gene_commentary_heading.text)   # NCBI Reference Sequences (RefSeq)

           if gene_commentary_heading_text != 'NCBI Reference Sequences (RefSeq)':
             if PRINT_HEADINGS: print("Skiping headings not equal to: 'NCBI Reference Sequences (RefSeq)'")
             continue

#      <Gene-commentary_type value="comment">254</Gene-commentary_type>
#      <Gene-commentary_heading>NCBI Reference Sequences (RefSeq)</Gene-commentary_heading>
           for gene_commentary1_comment in gene_commentary1.findall('Gene-commentary_comment'):
             for gene_commentary2 in gene_commentary1_comment.findall('Gene-commentary'):
#               print("gene_commentary2:",gene_commentary2)
               if PRINT_HEADINGS:
                 for gene_commentary_heading in gene_commentary2.findall('Gene-commentary_heading'):
                   print("Gene_commentary2_heading:",gene_commentary_heading.text)  # RefSeqs maintained independently of Annotated Genomes
               
#          <Gene-commentary_type value="comment">254</Gene-commentary_type>
#          <Gene-commentary_heading>RefSeqs maintained independently of Annotated Genomes</Gene-commentary_heading>
               for gene_commentary_products in gene_commentary2.findall('Gene-commentary_products'):
#                 print("*****gene_commentary_products:",gene_commentary_products)
                 for gene_commentary3 in gene_commentary_products.findall('Gene-commentary'):
#                   print("gene_commentary3:",gene_commentary3)

                   for gene_commentary_type in gene_commentary3.findall('Gene-commentary_type'):
                      gene_commentary_type_attrib = gene_commentary_type.attrib['value']
                   if PRINT_TYPE:                                      
                       print("Gene_commentary3_type:",gene_commentary_type.attrib['value'],gene_commentary_type.text)  # mRNA
                   if PRINT_HEADINGS:
                     for gene_commentary_heading in gene_commentary3.findall('Gene-commentary_heading'):
                       print("Gene_commentary3_heading:",gene_commentary_heading.text)  # mRNA Sequence
                       
                   if gene_commentary_type_attrib != 'mRNA': continue                       
                   for gene_commentary_version in gene_commentary3.findall('Gene-commentary_version'):
                     if gene_commentary_version.text != '3':
                       warn("For %s %s: Gene-commentary3_version, expected '3' but found: %s" %(gene_track_entrez_id,gene_name,gene_commentary_version.text))  # 3
                                                                    
                   
#              <Gene-commentary_type value="mRNA">3</Gene-commentary_type>
#              <Gene-commentary_heading>mRNA Sequence</Gene-commentary_heading>
#              <Gene-commentary_accession>NM_005160</Gene-commentary_accession>
#              <Gene-commentary_version>3</Gene-commentary_version>
#              .....
                   for gene_commentary_products2 in gene_commentary3.findall('Gene-commentary_products'):
                     for gene_commentary4 in gene_commentary_products2.findall('Gene-commentary'):
#                       print("gene_commentary4:",gene_commentary4)
                       for gene_commentary_type in gene_commentary4.findall('Gene-commentary_type'):
                           gene_commentary_type_attrib = gene_commentary_type.attrib['value']
                       if PRINT_TYPE:
                         print("Gene_commentary4_type:",gene_commentary_type.attrib['value'],gene_commentary_type.text)  # peptide
                           
                       if PRINT_HEADINGS:                           
                         for gene_commentary_accession in gene_commentary4.findall('Gene-commentary_accession'):
                           print("Gene_commentary4_accession:",gene_commentary_accession.text)   # eg: NP_000005
                         for gene_commentary_heading in gene_commentary4.findall('Gene-commentary_heading'):                       
                           print("Gene_commentary4_heading:",gene_commentary_heading.text)       # Product
                           
                       if gene_commentary_type_attrib != 'peptide': continue
                       for gene_commentary_version in gene_commentary4.findall('Gene-commentary_version'):
                         if gene_commentary_version.text != '2':
                           warn("For %s %s: Gene-commentary4_version, expected '2' but found: '%s'" %(gene_track_entrez_id,gene_name,gene_commentary_version.text)) # 2
                         

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
                  
                       for gene_commentary4_comment in gene_commentary4.findall('Gene-commentary_comment'):
                         for gene_commentary5 in gene_commentary4_comment.findall('Gene-commentary'):
#                          <Gene-commentary_type value="other">255</Gene-commentary_type>
#                          <Gene-commentary_heading>Related</Gene-commentary_heading>
#                             <Gene-commentary_heading>Related</Gene-commentary_heading>
                           if PRINT_HEADINGS:
                             for gene_commentary_heading in gene_commentary5.findall('Gene-commentary_heading'):
                               print("gene_commentary5_heading:",gene_commentary_heading.text)  # Related or UniProtKB (whereas for the previous one is: Conserved Domains )

# For UniProtKB  - but gives: "SystemError: too many statically nested blocks", so need to use XPath:
#                           for gene_commentary5_comment in gene_commentary5.findall('Gene-commentary_comment'):
#                             for gene_commentary6 in gene_commentary5_comment.findall('Gene-commentary'):
#                               for gene_commentary_source in gene_commentary6.findall('Gene-commentary_source'):
#                                 for other_source in gene_commentary_source.findall('Other-source'):
#                                   for other_source_src in other_source.findall('Other-source_src'):
#                                     for dbtag in other_source_src.findall('Dbtag'):
                           for dbtag in gene_commentary5.iterfind('Gene-commentary_comment/Gene-commentary/Gene-commentary_source/Other-source/Other-source_src/Dbtag'):
                                       for dbtag_db in dbtag.findall('Dbtag_db'):  #  UniProtKB/Swiss-Prot                                       
                                         dbtag_db_text = dbtag_db.text
                                         # print("Dbtag_db:",dbtag_db_text)
                                       if dbtag_db_text == 'UniProtKB/Swiss-Prot':
                                         for object_id_str in dbtag.iterfind('Dbtag_tag/Object-id/Object-id_str'):
                                           if PRINT_VALUE: print(dbtag_db_text+":",object_id_str.text)
                                           uniprot = object_id_str.text  # eg: P35626
#                                       for dbtag_tag in dbtag_db.findall('Dbtag_tag'):
#                                         for object_id in dbtag_tag.findall('Object-id'):
#                                           for object_id_str in object_id.findall('Object-id_str'): # eg: P01023
#                                             print(dbtag_db_text+":",object_id_str.text)

                             
#                           for gene_commentary_source in gene_commentary5.findall('Gene-commentary_source'):
#                             print("gene_commentary_source:",gene_commentary_source)
#                             for other_source in gene_commentary_source.findall('Other-source'):
#                               for other_source_src in other_source.findall('Other-source_src'):
#                                 for dbtag in other_source_src.findall('Dbtag'):
                                 
                           for dbtag in gene_commentary5.iterfind('Gene-commentary_source/Other-source/Other-source_src/Dbtag'):
                                   for dbtag_db in dbtag.findall('Dbtag_db'):   # Ensembl
#                                     print("Dbtag_db:",dbtag_db.text)
                                     dbtag_db_text = dbtag_db.text  # if Ensembl
                                   if dbtag_db_text == 'Ensembl':
                                     for object_id_str in dbtag.iterfind('Dbtag_tag/Object-id/Object-id_str'):
                                       if PRINT_VALUE: print(dbtag_db.text+":",object_id_str.text)
                                       ensembl_protein = object_id_str.text  # eg:  ENSP00000317578

#                                   for dbtag_tag in dbtag.findall('Dbtag_tag'):
#                                     print("* Dbtag_tag",dbtag_tag)
#                                     for object_id in dbtag_tag.findall('Object-id'):
#                                       print("** Object_id:",object_id)
#                                       for object_id_str in object_id.findall('Object-id_str'):  # ENSP00000317578
#                                         print("*** "+dbtag_db_text+":",object_id_str.text)
#                                       for object_id_id in object_id.findall('Object-id_id'):
#                                         print("*** "+dbtag_db.text+":",object_id_id.text)
                    
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

 
     fout2.write(gene_track_entrez_id +
      "\t"+gene_track_status_string +
      "\t"+gene_track_status_int +
      "\t"+current_entrez_id +
      "\t"+current_locus +
      "\t"+gene_name +
      "\t"+maploc +
      "\t"+hgnc +
      "\t"+ensembl_gene +
      "\t"+hprd +
      "\t"+omim +
      "\t"+vega +
      "\t"+ensembl_protein +
      "\t"+uniprot +
      "\t"+desc +  
      "\t"+synonyms +
      "\t"+summary+
      "\n"
      )
     gene_summaries_found_count += 1
     
     if gene_track_entrez_id in del entrez_to_genename_dict[gene_track_entrez_id]
     else warn("gene_track_entrez_id %s NOT found in the input entrez_to_genename_dict" %(gene_track_entrez_id))
       
     if PRINT_VALUE: print("#END\n")

   for key in entrez_to_genename_dict:
     warn("%s %s NOT returned from NCBI entrez query" %(key,entrez_to_genename_dict[key]))
     
   return gene_summaries_found_count
     
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
 BATCH_SIZE=2000 # number of ids to submit in one query (150 was too few, and probably caused the gate way error)
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



def process_all_genes_in_files():
 BATCH_SIZE=300 # number of ids to submit in one query.
 
 # indir = "postprocessing_R_results/"
 indir = "198_boxplots_for_Colm/analyses/"
 
 # Campbell is ensembl ids:
 # PIK3CA_5290_ENSG00000121879     AAK12_ENSG00000115977
 #  indir+"univariate_results_Campbell_v26_for36drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt",
 #  indir+"univariate_results_Campbell_v26_for36drivers_pancan_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt",
 
 # Achilles and Colt are Entrez ids:
 input_files=( 
   indir+"univariate_results_Achilles_v4_for36drivers_bytissue_kinome_combmuts_26Aug2016witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt",
   indir+"univariate_results_Achilles_v4_for36drivers_pancan_kinome_combmuts_26Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt",
   indir+"univariate_results_Colt_v2_for36drivers_bytissue_kinome_combmuts_15Aug2016_witheffectsize_and_zdiff_and_boxplotdata_mutantstate.txt"
  )
 genes_without_entrez_ids = []
 genes_without_summary = []
 entrez_to_genename_dict = dict()
 genes_processed = dict()
 
 is_first = True
 
 genes_processed_count = 0
 total_gene_summaries_found_count = 0

 fout1 = open("entrez_gene_full_details.xml","w")
 fout2 = open("entrez_gene_full_details.txt","w")
 
 dont_process = True
  
 for infile in input_files:
  with open(infile, "r") as fin:
   header = fin.readline() # Skip header line.
   
   for line in fin:
    cols = line.split("\t")
    names = cols[1].split("_")  # Target gene
# with transaction.atomic(): # Using atomic makes this script run in half the time, as avoids autocommit after each change
#  for g in Gene.objects.all().iterator():
    #print(g.gene_name, g.entrez_id)
#    if g.entrez_id=='' or g.entrez_id=='NoEntrezId':
#        genes_without_entrez_ids.append(g.gene_name)
#    else:    
#        entrez_to_genename_dict[g.entrez_id] = g.gene_name
    if names[1] not in genes_processed:
      if names[1] == '': genes_without_entrez_ids[names[0]]=True
      else:
        entrez_to_genename_dict[names[1]] = names[0]
        genes_processed[names[1]] = True
        #driver_text = '*DRIVER*' if g.is_driver else ''
        genes_processed_count += 1
        print(names[0],"=",names[1])

    if dont_process: # Skip until after '439921': # MXRA7, where failed due to: requests.exceptions.HTTPError: 502 Server Error: Bad Gateway for url: http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene
       if names[1] == '439921': # MXRA7
         dont_process = False
         print("Found last gene processed, so will start after this:",names[1])
         entrez_to_genename_dict.clear()
       continue
    
    # Request 100 interactions at a time, to reduce load on server
    if len(entrez_to_genename_dict) == BATCH_SIZE:
      total_gene_summaries_found_count += get_entrez_full(entrez_to_genename_dict, is_first, fout1, fout2)
      is_first = False

#      unmatched_genes += ('' if unmatched_genes == '' and unmatched == '' else ', ') + unmatched
           # print("GENE:\t%s\t%s" %(gene_name,entrez_summaries[entrez_id]))

#           genes_with_summary_count += 1
#        else:
#           genes_without_summary.append(gene_name)        
      entrez_to_genename_dict.clear()
#      break  # To STOP for now with this test run of 10.  
      #print("genes_processed_count:", genes_processed_count)
      
 if len(entrez_to_genename_dict) > 0: # Process any remaining genes as < BATCH_SIZE
   total_gene_summaries_found_count += get_entrez_full(entrez_to_genename_dict, is_first, fout1, fout2)

 fout1.close()
 fout2.close()
    
 print("Genes_processed: %d,  Gene_summaries_found: %d" %(genes_processed_count, total_gene_summaries_found_count))
 print("\nGenes_without_entrez_ids: %d:" %(len(genes_without_entrez_ids)) )
 print("\n".join(genes_without_entrez_ids))

      #gene_count = 0

if __name__ == "__main__":
    # process_all_genes_in_db()
    process_all_genes_in_files()    
    
    #get_entrez_summaries({'2064':'ERBB2', '7422':'VEGFA'},None,None)
    
    #test_post()


"""
Mac:cgdd sbridgett$ grep -v _version fetch_entrez_full_details_set1.err
* WARNING:  For 729706 $: Unexpected gene_track_status: discontinued
* WARNING:  For 729711 $: Unexpected gene_track_status: discontinued
* WARNING:  For 402207 $: Unexpected gene_track_status: discontinued
* WARNING:  For 729724 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100653050 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100288018 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100508408 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100131735 $: Unexpected gene_track_status: discontinued
* WARNING:  For 7441 $VPREB1: Unexpected Gene-ref DB str: IMGT/GENE-DB VPREB1
* WARNING:  For 652586 $: Unexpected gene_track_status: discontinued
* WARNING:  For 391764 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100653162 $: Unexpected gene_track_status: discontinued
* WARNING:  For 391767 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100652810 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100506705 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100509256 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100506877 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100507111 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100652822 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100653196 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100653311 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100507436 $MICA: Unexpected Gene-ref DB str: IMGT/GENE-DB MICA
* WARNING:  For 652119 $: Unexpected gene_track_status: discontinued
* WARNING:  For 650157 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100288657 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100288627 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100134409 $: Unexpected gene_track_status: discontinued
* WARNING:  For 391766 $: Unexpected gene_track_status: discontinued
* WARNING:  For 100134264 $: Unexpected gene_track_status: discontinued
* WARNING:  For 4277 $MICB: Unexpected Gene-ref DB str: IMGT/GENE-DB MICB
Traceback (most recent call last):

Mac:cgdd sbridgett$ grep -v _version fetch_entrez_full_details.err
* WARNING:  For 90462 $: Unexpected gene_track_status: discontinued
* WARNING:  For 442744 $: Unexpected gene_track_status: discontinued

"""