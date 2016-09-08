#!/bin/bash

IN="db.sqlite3"
OUT="all_dependencies.csv.gz"

# Just output the studies:
# SQL="select * from gendep_study;"

# To filter by ERBB2 and PANCAN:
# SQL="SELECT D.target, D.wilcox_p, D.effect_size, D.zdiff, D.interaction, D.pmid, D.histotype, G.ensembl_id, G.ensembl_protein_id, G.inhibitors FROM gendep_dependency D INNER JOIN gendep_gene G ON (D.target = G.gene_name) WHERE (D.driver = 'ERBB2' AND D.histotype = 'PANCAN') ORDER BY D.wilcox_p ASC;"
# SQL="SELECT D.target, D.wilcox_p, D.effect_size, D.zdiff, D.interaction, S.short_name AS study, D.histotype AS tissue, G.entrez_id, G.ensembl_id, G.ensembl_protein_id, G.inhibitors FROM gendep_dependency D INNER JOIN gendep_gene G ON (D.target = G.gene_name) INNER JOIN gendep_study S ON (S.pmid = D.pmid) WHERE (D.driver = 'ERBB2' AND D.histotype = 'PANCAN') ORDER BY D.wilcox_p ASC;"

# For all drivers and histotypes:
# For Driver's "H.alteration_considered", need to add:  "INNER JOIN gendep_gene H ON (D.driver = H.gene_name)"
SQL="SELECT D.driver, D.target, D.wilcox_p, D.effect_size, D.zdiff, D.interaction, S.short_name AS study, D.histotype AS tissue, G.entrez_id, G.ensembl_id, G.ensembl_protein_id, G.inhibitors FROM gendep_dependency D INNER JOIN gendep_gene G ON (D.target = G.gene_name) INNER JOIN gendep_study S ON (S.pmid = D.pmid) ORDER BY D.driver, D.wilcox_p ASC;"

# Instead of gzip or zip, could use 7zip which compresses more and can uncompress on Windows easily:
# Download p7zip for Linux from: https://sourceforge.net/projects/p7zip/files/p7zip/16.02/p7zip_16.02_x86_linux_bin.tar.bz2/download
# Or on MacOS with homebrew installed:   brew install p7zip
# The double quotes are needed around the $SQL:
sqlite3 -batch -header -csv $IN "$SQL" | gzip > $OUT
