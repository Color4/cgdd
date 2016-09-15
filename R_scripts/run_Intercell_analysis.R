# ================================== #
# Analysis code as described in
# "Large scale profiling of kinase
# dependencies in cancer cell lines"
# jamesc@icr.ac.uk, 3rd March 2016
# Modified by s.bridgett@qub.ac.uk, 26th Aug 2016
# ================================== #

# Need to have preprocessCore, gplots and mixtools installed.

# --------------------------------------------------- #
# Select dataset to process by uncommenting that line #
# --------------------------------------------------- #

# data_set <- "Campbell"  # Campbell et al (2016) - Kinase Dependencies in Cancer Cell Lines.
# data_set <- "Achilles"  # Cowley et al   (2014) - Loss of function screens in 216 cancer cell lines.
data_set <- "Colt"      # Marcotte et al (2016) - Breast cancer cell lines.
# data_set <- "Achilles_CRISPR" # New Achilles CRISPR-Cas9 data

# ----------------------------------------------------------- #
# Set output path on your computer                            #
# (the R_scripts and preprocessing are relative to this path) #
# ----------------------------------------------------------- #

# Eg: on Windows:
#setwd("C:/Users/HP/Django_projects/cgdd/postprocessing_R_results/")
# Eg: on Mac:
setwd("/Users/sbridgett/Documents/UCD/cgdd/postprocessing_R_results/")


# ------------------------------ #
# Common inputs for all datasets #
# ------------------------------ #

# Cell-line genotype files:
combmuts_func_file <- "../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_func_muts_v1.txt" # (indicates if there is a functional mutation)
combmuts_all_file <- "../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_all_muts_v1.txt"  # (indicates if there is any mutation)
combmuts_classes_file <- "../preprocess_genotype_data/genotype_output/GDSC1000_cnv_exome_func_mut_types_v1.txt" # (indicates mutation types: 1 or 2)


# ----------------------------------------------------- #
# Specify the Analysis specific input and results files #
# ------------------------------------------------------#

if (data_set == "Campbell") {
  print("Running Campbell ...")
  # pubmed_id <- "26947069" # Campbell(2016)  
  kinome_file <-  "../preprocess_genotype_data/rnai_datasets/Intercell_v18_rc4_kinome_cancergd.txt"
  tissues_file <- "../preprocess_genotype_data/rnai_datasets/Intercell_v18_rc4_kinome_cancergd_tissues.txt"
  # WAS: tissues_file <- "../data_sets/siRNA_Zscores/Intercell_v18_rc4_tissues_zp0_for_publication.txt"
  #   but bhanged "CERVICAL" to "CERVIX" to match the above new kinome_file, Sept 2016:
  
  uv_results_kinome_combmuts_pancan_file   <- "univariate_results_Campbell_v26_for36drivers_pancan_kinome_combmuts_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Campbell_v26_for36drivers_bytissue_kinome_combmuts_witheffectsize_and_zdiff.txt"

} else if (data_set == "Achilles") {
  print("Running Achilles ...")
  # pubmed_id <- "25984343" # Cowley(2014) for Achilles
  kinome_file  <- "../preprocess_genotype_data/rnai_datasets/Achilles_QC_v2.4.3_cancergd_with_entrezids.txt" # Uses entrezid instead of ensembl ids.
  tissues_file <- "../preprocess_genotype_data/rnai_datasets/Achilles_QC_v2.4.3_tissues.txt" # Treats PLEURA as separate tissue.

  uv_results_kinome_combmuts_pancan_file   <- "univariate_results_Achilles_v4_for36drivers_pancan_kinome_combmuts_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_v4_for36drivers_bytissue_kinome_combmuts_witheffectsize_and_zdiff.txt"

} else if (data_set == "Colt") {
  # NOTE: There are several ids with just number and '_EntrezNotFound':
  print("Running Achilles_Colt ...")  
  # pubmed_id <- "26771497" # Marcotte(2016) for Colt study
  kinome_file  <- "../preprocess_genotype_data/rnai_datasets/coltv2_zgarp_cancergd_reformatted.txt"  
  tissues_file <- "../preprocess_genotype_data/rnai_datasets/coltv2_zgarp_tissues.txt"   # All Colt data are breast tissues.

  # In Colt study only breast tissue - so only by-tissue anaylsis, no Pan-cancer:
  uv_results_kinome_combmuts_pancan_file   <- "NONE"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Colt_v2_for36drivers_bytissue_kinome_combmuts_witheffectsize_and_zdiff.txt"
  
} else if (data_set == "Achilles_CRISPR") {
  print("Running Achilles_CRISPR ...")
  # pubmed_id <- "27260156" # Achilles CRISPR(2016)
  kinome_file  <- "../preprocess_genotype_data/rnai_datasets/Achilles_v3.3.8_cancergd_with_entrezids.txt"
  tissues_file <- "../preprocess_genotype_data/rnai_datasets/Achilles_v3.3.8_tissues.txt"
  
  uv_results_kinome_combmuts_pancan_file   <- "univariate_results_Achilles_CRISPR_for36drivers_pancan_kinome_combmuts_witheffectsize_and_zdiff.txt"
  uv_results_kinome_combmuts_bytissue_file <- "univariate_results_Achilles_CRISPR_for36drivers_bytissue_kinome_combmuts_witheffectsize_and_zdiff.txt"  
  
} else {
  stop(paste("ERROR: Invalid data_set: '",data_set,"' but should be 'Campbell', 'Achilles' or 'Colt'"))
}

cat("Variables set to:\ndata_set:",data_set,"\nkinome_file:",kinome_file,"\ntissues_file:",tissues_file,"\n")  # Using cat() as print(paste(....)) does not interpret \n as newline.


# ------------------------------ #
# Source the Intercell functions #
# ------------------------------ #

# ******* Always need to set the 'data_set' value before sourcing the Intercell_functions, as it is used to set the tissue lists and plot colours.

source_script <- "../R_scripts/Intercell_analysis_functions.R";    # source_file_info <- file.info(source_script); 
source(source_script); # returns: size, isdir, mode, mtime, ctime, atime = integer of class "POSIXct": modification, ‘last status change’ and last access times. So compare 'mtime' with previous mtime. Better to get info before reading the file, as might change between.


# ---------------- #
# Read in the data
# ---------------- #

kinome_combmuts <- read_rnai_mutations(
	rnai_file=kinome_file,
	func_muts_file=combmuts_func_file,
	all_muts_file=combmuts_all_file,
	mut_classes_file=combmuts_classes_file,
	tissues_file=tissues_file
	)

# -------------------------------- #
# Run the set of hypothesis tests
# on the kinome z-score data sets
# -------------------------------- #

if (data_set != "Colt") {
	# Driver gene mutations in combined histotypes - No Pan-cancer for Colt as it is only Breast cancer cell lines.
	uv_results_kinome_combmuts <- run_univariate_tests(
		zscores=kinome_combmuts$rnai,
		mutations=kinome_combmuts$func_muts,
		all_variants=kinome_combmuts$all_muts,
		sensitivity_thresholds=kinome_combmuts$rnai_iqr_thresholds,
		min_cell_lines=5   # This is 5 for PANCAN (is 3 for Within Tissue)
		)
	write.table(
		uv_results_kinome_combmuts,
		file=uv_results_kinome_combmuts_pancan_file,
		sep="\t",
		quote=FALSE,
		row.names=FALSE
		)
}

# Driver gene mutations in separate histotypes (the uv_results_...by_tissue uses: min_cell_lines=3)
uv_results_kinome_combmuts_bytissue <- run_univariate_test_bytissue(kinome_combmuts)
write.table(
	uv_results_kinome_combmuts_bytissue,
	file=uv_results_kinome_combmuts_bytissue_file,
	sep="\t",
	quote=FALSE,
	row.names=FALSE
)


# ------------------------------ #
# (Re-)load in the results files
# ------------------------------ #

if (data_set != "Colt") {
	uv_results_kinome_combmuts <- read.table(
		file=uv_results_kinome_combmuts_pancan_file,
		header=TRUE,
		sep="\t",
		stringsAsFactors=FALSE
		)
}		

uv_results_kinome_combmuts_bytissue <- read.table(
	file=uv_results_kinome_combmuts_bytissue_file,
	header=TRUE,
	sep="\t",
	stringsAsFactors=FALSE
	)

# ----------------------------------------- #
# Add the boxplot data to the result files  #
# ----------------------------------------- #

if (data_set != "Colt") {
	# Add the combmuts boxplot data, which will be coloured by tissue
	# select associations where wilcox.p <= 0.05 and CLES > =0.65

	fileConn<-file(open="w", paste0( sub("\\.txt$","",uv_results_kinome_combmuts_pancan_file), "_and_boxplotdata_mutantstate.txt") ) # Need "\\." to correctly escape the dot in regexp in R
	write_box_dot_plot_data(
		results=as.data.frame(
			uv_results_kinome_combmuts[which(
				uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
				uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
				),]
			),
		zscores=kinome_combmuts$rnai,
		mutation.classes=kinome_combmuts$mut_classes, # SJB - I think this is the mutation types.
		mutations=kinome_combmuts$func_muts,
		exclusions=kinome_combmuts$all_muts,
		tissues=kinome_combmuts$tissues,
		fileConn = fileConn,
		writeheader=TRUE,
		tissue_actual_names=legend_actual_tissues
		)
	close(fileConn) # caller should close the fileConn	
}

	
# Write the combmuts boxplot data for separate histotypes
# select associations where wilcox.p <= 0.05 and CLES > =0.65

fileConn<-file(open="w", 
paste0( sub("\\.txt$","",uv_results_kinome_combmuts_bytissue_file), "_and_boxplotdata_mutantstate.txt") ) # Output file. Needs "w" otherwise cat(...) overwrites previous cat()'s rather than appending. To open and append to existing file use "a"
tissues <- levels(as.factor(uv_results_kinome_combmuts_bytissue$tissue))
write_header <- TRUE
for(this_tissue in tissues){
	rows_to_plot <- which(
		kinome_combmuts$tissues[,this_tissue] == 1
		)
	write_box_dot_plot_data(
		results=as.data.frame(
			uv_results_kinome_combmuts_bytissue[which(
				uv_results_kinome_combmuts_bytissue[,"wilcox.p"] <= 0.05 &
				uv_results_kinome_combmuts_bytissue[,"CLES"] >= 0.65 & # SJB Added this effect_size test
				uv_results_kinome_combmuts_bytissue[,"tissue"] == this_tissue
				),]
			),
		zscores=kinome_combmuts$rnai[rows_to_plot,],
		mutation.classes=kinome_combmuts$mut_classes[rows_to_plot,],
		mutations=kinome_combmuts$func_muts[rows_to_plot,],
		exclusions=kinome_combmuts$all_muts[rows_to_plot,],
		tissues=kinome_combmuts$tissues[rows_to_plot,],
		fileConn=fileConn,
		writeheader=write_header,
		tissue_actual_names=legend_actual_tissues,
		)
	write_header <- FALSE # As only write the header line for first call of the above write_boxplot_data
}
close(fileConn) # caller should close the fileConn





# ------------------------------------------------------------- #
# Can optionally plot the boxplots and legend as png images     #
# BUT this isn't needed for the CancerGD web-interface as it    #
# plots the boxplot data output above using javascript and SVG. #
# ------------------------------------------------------------- #

# Plot all combmuts results coloured by tissue
# select associations where wilcox.p <= 0.05 and CLES > =0.65
#source(source_script)
#debug(make_mini_box_dot_plots)
#make_mini_box_dot_plots(
#	results=as.data.frame(
#		uv_results_kinome_combmuts[which(
#			uv_results_kinome_combmuts[,"wilcox.p"] <= 0.05 &
#			uv_results_kinome_combmuts[,"CLES"] >= 0.65 # SJB Added this effect_size test
#			),]
#		),
#	zscores=kinome_combmuts$rnai,
#	mutation.classes=kinome_combmuts$mut_classes,
#	mutations=kinome_combmuts$func_muts,
#	exclusions=kinome_combmuts$all_muts,
#	tissues=kinome_combmuts$tissues,
#	prefix_for_filename=combined_histotypes_boxplot_dir,
#	suffix_for_filename="PANCAN", # SJB WAS: "allhistotypes",
#	pubmed_id_for_filename=pubmed_id, # Added by SJB 
#	tissue_pretty_names=legend_pretty_tissues,
#	tissue_actual_names=legend_actual_tissues,
#	tissue_cols=legend_col
#	)

	
# Plot combmuts results for separate histotypes
# select associations where wilcox.p <= 0.05
#tissues <- levels(as.factor(uv_results_kinome_combmuts_bytissue$tissue))
#for(this_tissue in tissues){
#	rows_to_plot <- which(
#		kinome_combmuts$tissues[,this_tissue] == 1
#		)
#	make_mini_box_dot_plots(
#		results=as.data.frame(
#			uv_results_kinome_combmuts_bytissue[which(
#				uv_results_kinome_combmuts_bytissue[,"wilcox.p"] <= 0.05 &
#				uv_results_kinome_combmuts_bytissue[,"CLES"] >= 0.65 & # SJB Added this effect_size test
#				uv_results_kinome_combmuts_bytissue[,"tissue"] == this_tissue
#				),]
#			),
#		zscores=kinome_combmuts$rnai[rows_to_plot,],
#		mutation.classes=kinome_combmuts$mut_classes[rows_to_plot,],
#		mutations=kinome_combmuts$func_muts[rows_to_plot,],
#		exclusions=kinome_combmuts$all_muts[rows_to_plot,],
#		tissues=kinome_combmuts$tissues[rows_to_plot,],
#		prefix_for_filename=separate_histotypes_boxplot_dir,
#		suffix_for_filename=this_tissue,
#		pubmed_id_for_filename=pubmed_id, # Added by SJB
#		tissue_pretty_names=legend_pretty_tissues,
#		tissue_actual_names=legend_actual_tissues,
#		tissue_cols=legend_col
#		)
#}


# make_legends()

