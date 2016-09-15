# ====================================== #
# Analysis functions used for univariate
# analyses in the Intercell II work
# jamesc@icr.ac.uk, 11th March 2014
# ====================================== #

# Added the jsonlite package:
#   install.packages("jsonlite", repos="http://cran.r-project.org")


require("preprocessCore")
require(gplots)
require(mixtools)

# require(jsonlite) # Added by SJB - no longer needed.

# Define colours used for plotting
# "#C9DD03" green
# "#FFD602" yellow
# "#F9A100" orange
# "#EE7EA6" pink
# "#A71930" red
# "#CCCCCC" grey
# "#726E20" olive
# "#6E273D" damson
# "#F00034" brightred
# "#ADAFAF" lightgrey
# "#003D4C" blue


# icrpal <- palette(c("#C9DD03", "#FFD602", "#F9A100", "#EE7EA6", "#A71930", "#CCCCCC","#726E20" , "#6E273D", "#F00034", "#ADAFAF", "#003D4C"))

# SJB - Achilles:
# "HEADNECK" "CERVICAL" are not in Achilles - so need to comment them out below as mini_boxplot uses legend_actual_tissues
# Added for Achilles: HAEMATOPOIETIC_AND_LYMPHOID_TISSUE, INTESTINE, KIDNEY, LIVER, PROSTATE, SKIN, SOFT_TISSUE, STOMACH, URINARY_TRACT
# Achilles - Numbers of celllines for each tissue type: BONE=6,  BREAST=12, CENTRAL_NERVOUS_SYSTEM=34, ENDOMETRIUM=2, HAEMATOPOIETIC_AND_LYMPHOID_TISSUE=30, INTESTINE=21, KIDNEY=10, LIVER=1, LUNG=23, OESOPHAGUS=10, OVARY=29, PANCREAS=17, PROSTATE=3, SKIN=7, SOFT_TISSUE=2, STOMACH=4, URINARY_TRACT=3
# In "legend_pretty_tissues", "Bone" was previously "Osteosarcoma", but changed in Aug 2016 as Achilles includes non-osteoscarcoma bone tumor cell-lines.
# Changed from "Cervical" to "Cervicx" in Sept 2016.

if (data_set == "Campbell") {	
  legend_pretty_tissues = c(
	"Bone",
	"Breast",
	"Lung",
	"Head & Neck",
	"Pancreas",
#	"Cervical",
	"Cervicx",
	"Ovary",
	"Esophagus",
	"Endometrium",
	"CNS"
	)
  legend_actual_tissues = c(
	"BONE",
	"BREAST",
	"LUNG",
	"HEADNECK",
	"PANCREAS",
#	"CERVICAL",
	"CERVIX",
	"OVARY",
	"OESOPHAGUS",
	"ENDOMETRIUM",
	"CENTRAL_NERVOUS_SYSTEM"
	)
  legend_col=c(
	"yellow",
	"deeppink",
	"darkgrey",
	"firebrick4",
	"purple",
	"blue",
	"cadetblue",
	"green",
	"orange",	
	"darkgoldenrod4"
	)
	
} else if (data_set == "Achilles") {
  legend_pretty_tissues = c(
	"Bone",
	"Breast",
	"Lung",
#	"Head & Neck",
	"Pancreas",
#	"Cervical",
	"Ovary",
	"Esophagus",
	"Endometrium",
	"CNS",
	"Blood & Lymph",
    "Large Intestine", # Updated from "Intestine" Aug 2016,
	"Kidney",
	"Liver",
    "Pleura", # Added Aug 2016	
	"Prostate",
	"Skin",
	"Soft tissue",
	"Stomach",
	"Urinary tract",
    "Other"	  # Added Aug 2016	
	)	
  legend_actual_tissues = c(
	"BONE",
	"BREAST",
	"LUNG",
#	"HEADNECK",
	"PANCREAS",
#	"CERVICAL",
	"OVARY",
	"OESOPHAGUS",
	"ENDOMETRIUM",
	"CENTRAL_NERVOUS_SYSTEM",
	"HAEMATOPOIETIC_AND_LYMPHOID_TISSUE",
    "LARGE_INTESTINE", # Updated from "INTESTINE" Aug 2016
	"KIDNEY",
	"LIVER",
    "PLEURA", # Added Aug 2016
	"PROSTATE",
	"SKIN",
	"SOFT_TISSUE",
	"STOMACH",
	"URINARY_TRACT",
    "OTHER"	  # Added Aug 2016
	)	
  legend_col=c(
	"yellow",    # Bone
	"deeppink",  # Breast
	"darkgrey",  # Lung
#	"firebrick4", 
	"purple",    # Pancreas
#	"blue",
	"cadetblue", # Ovary
	"green",     # Oesophagus
	"orange",    # Endometrium
	"darkgoldenrod4", # CNS
	"darkred",   # Blood & Lymph
    "saddlebrown", # Large Intestine
	"indianred",
	"slategray",
  "slategray",  # **** Still to fix this colour for: "Pleura", # Added Aug 2016	
	"turquoise",  # Prostate
	"peachpuff",  # Skin
	"lightgrey",  # Soft tissue
    "black",      # Stomach
    "yellowgreen",
"slategray" # **** Still to fix colour for: "Other"	  # Added Aug 2016	    
	)

} else if(data_set == "Colt") {	  # Only Breast, but dummy BONE added in tissues file for plotting
  legend_pretty_tissues = c(
	"Breast"
	)
  legend_actual_tissues = c(
	"BREAST"
    )
  legend_col=c(
	"deeppink"
    )

} else if(data_set == "Achilles_CRISPR") {
  legend_pretty_tissues = c(
    "Bone",
    "Breast",
    "Blood & Lymph",
    "Large Intestine",
    "Lung",
    "Ovary",
    "Pancreas",
    "Prostate",
    "Skin",
    "Soft tissue"  
    )
  legend_actual_tissues = c(
    "BONE",
    "BREAST",
    "HAEMATOPOIETIC_AND_LYMPHOID_TISSUE",
    "LARGE_INTESTINE",
    "LUNG",
    "OVARY",
    "PANCREAS",
    "PROSTATE",
    "SKIN",
    "SOFT_TISSUE"
    )
  legend_col=c(
	"yellow",   # Bone
	"deeppink", # Breast 
	"darkred",  # Blood & Lymph
	"saddlebrown", # Large Intestine
	"darkgrey", # Lung
    "cadetblue", # Ovary	
	"purple",   # Pancreas
	"turquoise", # Prostate
	"peachpuff",  # Skin
	"lightgrey"  # Soft tissue
  )
	
} else {
  stop(paste("ERROR: Invalid data_set: '",data_set,"' but should be 'Campbell', 'Achilles' or 'Colt'"))
  }
	
names(legend_col) <- legend_actual_tissues

# SJB - list of 21 copied from the "run_intercell_analysis.R" downloaded from github GeneFunctionTeam repo on 12 March 2016
# Define the set of 23 genes with
# good represention (≥ 7 mutants).
# This list can be used to filter
# the complete set of tests

# On 15 Aug 2016, The gene 	"NOTCH2_4853_ENSG00000134250" was removed from this list, and 14 new genes added.





cgc_vogel_genes_with_n7 <- c(
	"CCND1_595_ENSG00000110092",
	"CDKN2A_1029_ENSG00000147889",
	"EGFR_1956_ENSG00000146648",
	"ERBB2_2064_ENSG00000141736",
	"GNAS_2778_ENSG00000087460",
	"KRAS_3845_ENSG00000133703",
	"SMAD4_4089_ENSG00000141646",
	"MDM2_4193_ENSG00000135679",
	"MYC_4609_ENSG00000136997",
	"NF1_4763_ENSG00000196712",
	"NRAS_4893_ENSG00000213281",
	"PIK3CA_5290_ENSG00000121879",
	"PTEN_5728_ENSG00000171862",
	"RB1_5925_ENSG00000139687",
	"MAP2K4_6416_ENSG00000065559",
	"SMARCA4_6597_ENSG00000127616",
	"STK11_6794_ENSG00000118046",
	"TP53_7157_ENSG00000141510",
	"ARID1A_8289_ENSG00000117713",
	"FBXW7_55294_ENSG00000109670",
	"BRAF_673_ENSG00000157764",    # Added BRAF on 14 April 2016 for future runs
	"CDH1_999_ENSG00000039068",    # Added CDH1 on 15 April 2016 for future runs
	"NCOR1_9611_ENSG00000141027",  # Added NCOR1 on 15 Aug 2016 for future runs
	"RNF43_54894_ENSG00000108375", # Added NCOR1 on 15 Aug 2016 for future runs 
	"BCOR_54880_ENSG00000183337",
	"EP300_2033_ENSG00000100393",
	"CDKN2C_1031_ENSG00000123080",
	"PIK3R1_5295_ENSG00000145675", 
	"KDM6A_7403_ENSG00000147050",
	"ASXL1_171023_ENSG00000171456",
	"MSH2_4436_ENSG00000095002",
	"ARID1B_57492_ENSG00000049618",
	"APC_324_ENSG00000134982",
	"CTNNB1_1499_ENSG00000168036",
	"BRCA2_675_ENSG00000139618",
	"MSH6_2956_ENSG00000116062"    # Added NCOR1 on 15 Aug 2016 for future runs 
	)
	
	
# Function to read in data, find the intersecting
# rownames and return a list of dataframes with 
# the common cell lines.
# Added 10th Dec 2014 to stop the data preprocessing
# getting out of hand.
read_rnai_mutations <- function(
	rnai_file,
	func_muts_file,
	all_muts_file,
	mut_classes_file,
	tissues_file
	){

	
	rnai <- read.table(
		file=rnai_file,
		header=TRUE,
		sep="\t",
		row.names=1
		)
	
	rnai_qn <- t(normalize.quantiles(t(rnai)))
	rownames(rnai_qn) <- rownames(rnai)
	colnames(rnai_qn) <- colnames(rnai)
	
	func_muts <- read.table(
		file=func_muts_file,
		sep="\t",
		header=TRUE,
		row.names=1
		)

	all_muts <- read.table(
		file=all_muts_file,
		header=TRUE,
		sep="\t",
		row.names=1
		)

	mut_classes <- read.table(
		file=mut_classes_file,
		header=TRUE,
		sep="\t",
		row.names=1
		)
	
	tissues <- read.table(
		file=tissues_file,
		header=TRUE,
		sep="\t",
		row.names=1
		)
	
	common_celllines <- intersect(
		rownames(rnai),
		rownames(func_muts)
		)

	common_celllines <- intersect(
		common_celllines,
		rownames(tissues)
		)


	
	i <- NULL
	row.index <- NULL
	rnai_muts_cmn <- NULL
	rnai_qn_muts_cmn <- NULL
	func_muts_rnai_cmn <- NULL
	all_muts_rnai_cmn <- NULL
	mut_classes_rnai_cmn <- NULL
	tissues_rnai_cmn <- NULL
	for(i in seq(1:length(common_celllines))){
		# rnai subset
		row.index <- NULL
		row.index <- which(rownames(rnai) == common_celllines[i])
		rnai_muts_cmn <- rbind(
			rnai_muts_cmn,
			rnai[row.index,]
		)
		# rnai_qn subset
		row.index <- NULL
		row.index <- which(rownames(rnai_qn) == common_celllines[i])
		rnai_qn_muts_cmn <- rbind(
			rnai_qn_muts_cmn,
			rnai_qn[row.index,]
		)
		# func_muts subset
		row.index <- NULL
		row.index <- which(rownames(func_muts) == common_celllines[i])
		func_muts_rnai_cmn <- rbind(
			func_muts_rnai_cmn,
			func_muts[row.index,]
		)
		# all_muts subset
		row.index <- NULL
		row.index <- which(rownames(all_muts) == common_celllines[i])
		all_muts_rnai_cmn <- rbind(
			all_muts_rnai_cmn,
			all_muts[row.index,]
		)
		# mut_classes subset
		row.index <- NULL
		row.index <- which(rownames(mut_classes) == common_celllines[i])
		mut_classes_rnai_cmn <- rbind(
			mut_classes_rnai_cmn,
			mut_classes[row.index,]
		)
		# tissues_rnai subset
		row.index <- NULL
		row.index <- which(rownames(tissues) == common_celllines[i])
		tissues_rnai_cmn <- rbind(
			tissues_rnai_cmn,
			tissues[row.index,]
		)
	}
	rownames(rnai_muts_cmn) <- common_celllines
	rownames(func_muts_rnai_cmn) <- common_celllines
	rownames(all_muts_rnai_cmn) <- common_celllines
	rownames(mut_classes_rnai_cmn) <- common_celllines
	rownames(tissues_rnai_cmn) <- common_celllines
	
	# calculate inter-quartile range (iqr) lower fence values
	# as a threshold for sensitivity. Do for the rnai and rnai_qn
	# data sets
	
	rnai_iqr_thresholds <- NULL
	i <- NULL
	for(i in 1:ncol(rnai)){
		rnai_iqr_stats <- quantile(rnai[,i], na.rm=TRUE)
		rnai_iqr_thresholds[i] <- rnai_iqr_stats[2] - 	((rnai_iqr_stats[4] - rnai_iqr_stats[2]) * 1.5)
	}
	names(rnai_iqr_thresholds) <- colnames(rnai)
	
	rnai_qn_iqr_thresholds <- NULL
	i <- NULL
	for(i in 1:ncol(rnai_qn)){
		rnai_qn_iqr_stats <- quantile(rnai_qn[,i], na.rm=TRUE)
		rnai_qn_iqr_thresholds[i] <- rnai_qn_iqr_stats[2] - 	((rnai_qn_iqr_stats[4] - rnai_qn_iqr_stats[2]) * 1.5)
	}
	names(rnai_qn_iqr_thresholds) <- colnames(rnai_qn)


	return(
		list(
			rnai=rnai_muts_cmn,
			rnai_qn=rnai_qn_muts_cmn,
			func_muts=func_muts_rnai_cmn,
			all_muts=all_muts_rnai_cmn,
			mut_classes=mut_classes_rnai_cmn,
			rnai_qn_iqr_thresholds=rnai_qn_iqr_thresholds,
			rnai_iqr_thresholds=rnai_iqr_thresholds,
			tissues=tissues_rnai_cmn
			)
		)
}


# This is the further revised code from Colm (28 April 2016) which includes the Delta-Score (and effect size test, and without spearman, etc):
# isByTissue parameter as using  
run_univariate_tests <- function(
	zscores,
	mutations,
	all_variants,
	sensitivity_thresholds=NULL,
	nperms=1000000,
	alt="less",
	min_cell_lines   # Added by SJB, Sept 2016. 3 or 5
	){	
	
	zscores <- as.matrix(zscores)
	mutations <- as.matrix(mutations)
	all_variants <- as.matrix(all_variants)
	
	work_count <- 0  # SJB added
	results <- NULL
	i <- NULL
	for(i in seq(1:length(colnames(mutations)))){

#       Skip if driver mutation is NOT in the above list of 36 genes for the Achilles and the Colt data	
#       Added by SJB to speed up initialy analysis of Achilles data by focusing in the 36 genes.
#	    if ( !(colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
#       or change to Skip if driver mutation IS in the above list of 36 genes - as they are already processed.
	    if ( !(colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
			# print(paste(toString(i),"skipping:", colnames(mutations)[i]))
			next
		}
        work_count <- work_count + 1
		print(paste(toString(i),"WORKING ON:",toString(work_count),colnames(mutations)[i]))
	
		grpA <- which(mutations[,i] > 0)
		
		#gene <- strsplit(
		#	colnames(mutations)[i],
		#	"_"
		#	)[[1]][1]
		gene <- colnames(mutations)[i]
		
		
		# grpB includes cell lines with no reported mutations at all
		# in gene...
		grpB <- which(all_variants[,gene] == 0)
		
		# skip if nA < 3 as we are never going to
		# consider anything based on n=2
#		if(length(grpA) < 3 | length(grpB) < 3){  # Changed by SJB, Sep 2016, to the line below:
		if(length(grpA) < min_cell_lines | length(grpB) < min_cell_lines){
			next
		}
		
		j <- NULL
		for(j in seq(1:length(colnames(zscores)))){
			ascores <- na.omit(zscores[grpA,j])
            bscores <- na.omit(zscores[grpB,j])
			nA <- length(ascores)
			nB <- length(bscores)
#			if(nA < 3){ # Should I also change this to: nA < min_cell_lines ?
			if(nB < min_cell_lines){ # Should I also change this to: nB < min_cell_lines ?
				next
			}
#			if(nB < 3){ # Should I also change this to: nB < min_cell_lines ?
			if(nB < min_cell_lines){ # Should I also change this to: nB < min_cell_lines ?
				next
			}
		    wilcox.p <- NA
			try(
				test <- wilcox.test(
					ascores,
					bscores,
					alternative=alt
				)
			)
			wilcox.p <- test$p.value
			cles <- 1-(test$statistic/(nA*nB))
			
			marker <- colnames(mutations)[i]
			target <- colnames(zscores)[j]
            nMin <- min(nA,nB)
            zA <- median(ascores)
            zB <- median(bscores)
            zDiff <- zA - zB
			# Output the result if min sample size is 2 or more
			if(nMin > 2){
				results <- rbind(
					results,
					c(
						marker,
						target,
						nA,
						nB,
						wilcox.p,
                        cles,
                        zA,
                        zB,
                        zDiff
					)
				)
			}
		}
	}
	
	if(is.null(nrow(results))){
		return(NULL)
	}
	
	colnames(results) <- c(
		"marker",
		"target",
		"nA",
		"nB",
		"wilcox.p",
		"CLES",
        "zA",
        "zB",
        "ZDiff"
	)
	
	return(results)
	
}




# This is the revised code from Colm (17 Mar 2016) which include the effect size test, and without spearman, etc:
run_univariate_tests_17March2016 <- function(
	zscores,
	mutations,
	all_variants,
	sensitivity_thresholds=NULL,
	nperms=1000000,
	alt="less"
	){
	
	
	zscores <- as.matrix(zscores)
	mutations <- as.matrix(mutations)
	all_variants <- as.matrix(all_variants)
	
	
	results <- NULL
	i <- NULL
	for(i in seq(1:length(colnames(mutations)))){

#       Skip if driver mutation is NOT in the above list of 21 genes for the Achilles and the Colt data	
#       Added by SJB to speed up initialy analysis of Achilles data by focusing in the 21 genes.
#	    if ( !(colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
#       or change to Skip if driver mutation IS in the above list of 21 genes - as they are already processed.
	    if ( !(colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
			print(paste(toString(i),"skipping:", colnames(mutations)[i]))
			next
		}

		print(paste(toString(i),"working on:", colnames(mutations)[i]))
		
		grpA <- which(mutations[,i] > 0)
		
		#gene <- strsplit(
		#	colnames(mutations)[i],
		#	"_"
		#	)[[1]][1]
		gene <- colnames(mutations)[i]
		
		
		# grpB includes cell lines with no reported mutations at all
		# in gene...
		grpB <- which(all_variants[,gene] == 0)
		
		# skip if nA < 3 as we are never going to
		# consider anything based on n=2
		if(length(grpA) < 3 | length(grpB) < 3){
			next
		}
		
		j <- NULL
		for(j in seq(1:length(colnames(zscores)))){
			
						
			# skip if we have no viability measurements
			# in one or other group
			if(length(na.omit(zscores[grpA,j])) < 3){
				next
			}
			if(length(na.omit(zscores[grpB,j])) < 3){
				next
			}
			
		wilcox.p <- NA
			try(
				test <- wilcox.test(
					zscores[grpA,j],
					zscores[grpB,j],
					alternative=alt
				)
			)
			wilcox.p <- test$p.value
			cles <- 1-(test$statistic/(length(zscores[grpA,j])*length(zscores[grpB,j])))
			
			marker <- colnames(mutations)[i]
			target <- colnames(zscores)[j]
			nA <- length(zscores[grpA,j])
			nB <- length(zscores[grpB,j])
            nMin <- min(nA,nB)
			# Output the result if min sample size is 2 or more
			if(nMin > 2){
				results <- rbind(
					results,
					c(
						marker,
						target,
						nA,
						nB,
						wilcox.p,
                        cles
					)
				)
			}
		}
	}
	
	if(is.null(nrow(results))){
		return(NULL)
	}
	
	colnames(results) <- c(
		"marker",
		"target",
		"nA",
		"nB",
		"wilcox.p",
		"CLES"
	)
	
	return(results)
	
}



run_univariate_test_bytissue <- function(x){
	
	tissue_types <- colnames(x$tissues)
	
	#print("A")
	#print(x)
	print(tissue_types)
	uv_results_bytissue <- NULL
	tissue <- NULL
	#print("B")
	for(tissue in tissue_types){
		print(paste("\nProcessing tissue:",tissue,"..."))
		cellline_count <- sum(
			x$tissues[,tissue]
			)
	#	print("D")
		if(cellline_count < 5){
		    print(paste("  Skipping tissue:",tissue,"as it has less than 5 cell lines."))
			next
		}
	#	print("E")
		tissue_rows <- which(
			x$tissues[,tissue] == 1
			)
	#	print("F")
		temp_results <- NULL
		temp_results <- run_univariate_tests(
			zscores=x$rnai[tissue_rows,],
			mutations=x$func_muts[tissue_rows,],
			all_variants=x$all_muts[tissue_rows,],
			sensitivity_thresholds=x$rnai_iqr_thresholds,
			min_cell_lines=3   # This is 5 for PANCAN, but is still 3 for ByTissue
			)
	#	print("G")
		if(is.null(nrow(temp_results))){
			print(paste("Skipping ", tissue, " - no results", sep=""))
			next
		}
	#	print("H")
		temp_results <- cbind(
			temp_results,
			rep(tissue, times=nrow(temp_results))
			)
	#	print("I")
		uv_results_bytissue <- rbind(
			uv_results_bytissue,
			temp_results
			)
	}
	#print("J")
	colnames(
		uv_results_bytissue
		)[ncol(
			uv_results_bytissue
			)
			] <- "tissue"
	return(uv_results_bytissue)
}


make_legends <- function(){
    #legend(xpd=TRUE, "topright", inset=c(-0.41,0), legend=tissue_pretty_names, fill=tissue_cols, cex=0.75 )  # was: x=1, y=1
    # where:
    #   tissue_pretty_names <- legend_pretty_tissues
    #   tissue_cols <- legend_col

	# The parameters used in the cgdd website are: 	w16_cex8 (ie. w=1.6, cex 0.8)
	png(filename=paste0("Legend_PMID", pubmed_id, ".png"),
		# width=5.3, height=4.5, units="in", res=96)
		# width=4.0, height=4.5, units="in", res=96)
		width=1.6, height=4.0, units="in", res=96) # was: width=1.5,
		# width=400, height=400) # default is pixils: , units="in"
		#  res = .... defaults to 72. The smaller this number, the larger the plot area in inches, and the smaller the text relative to the graph itself.

	par(bty="n", mai=c(0.1, 0.1, 0.1, 0.1) ) # SJB: was: width=2.5, height=3, units="in", res=96
	#par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 1.4)) # <-- for legend at right.  SJB: original was: width=2.5, height=3

    plot(1, type="n", axes=FALSE, xlab="", ylab="") # creates an empty plot
    legend("center", legend=legend_pretty_tissues, fill=legend_col, cex=0.8 )  # was: x=1, y=1, was: cex=0.75
	# horiz=TRUE, 
	dev.off()
	
# Alternatively for horizontal legends with several rows could use:
#  ggplot2 ...  guides(col = guide_legend(nrow = N))
#   http://127.0.0.1:18284/library/ggplot2/html/guide_legend.html
#	http://osdir.com/ml/ggplot2/2013-02/msg00033.html
#   http://r.789695.n4.nabble.com/Re-Legend-formatting-ggplot2-td4674812.html
#  http://www.sthda.com/english/wiki/ggplot2-legend-easy-steps-to-change-the-position-and-the-appearance-of-a-graph-legend-in-r-software
#   https://groups.google.com/forum/#!topic/ggplot2/ZAAGS6AJIaM
# To just plot the legends in ggplot2:
#   http://stackoverflow.com/questions/12041042/how-to-plot-just-the-legends-in-ggplot2
#   https://stevencarlislewalker.wordpress.com/2012/05/09/plotting-individual-pieces-of-a-ggplot2-plot-object/
#   http://brazenly.blogspot.co.uk/2014/04/r-playing-with-legends-of-graph-using.html
#   **GOOD: http://zevross.com/blog/2014/08/04/beautiful-plotting-in-r-a-ggplot2-cheatsheet-3/
#   http://docs.ggplot2.org/current/guide_legend.html
#   http://stackoverflow.com/questions/6432646/wrap-horizontal-legend-across-multiple-rows
}

make_mini_box_dot_plots <- function(
	results,
	zscores,
	mutation.classes,
	mutations,
	exclusions,
	tissues,
	prefix_for_filename,
	suffix_for_filename,
	pubmed_id_for_filename, # <-- Added by SJB for Achilles
	tissue_pretty_names,
	tissue_actual_names,
	tissue_cols,
	response_type="Z-score"
	){
	
	i <- NULL
	for(i in 1:nrow(results)){
# SJB commented out the following test, as the new effect_size (CLES) function doesn't output this 'med.grpA.med.grpB' result:
#		if(is.na(results$med.grpA.med.grpB[i])){
#			next
#		}


		if(results$nA[i] > 2){
			marker_gene <- strsplit(results$marker[i], "_")[[1]][1]
			target_gene <- strsplit(results$target[i], "_")[[1]][1]
			
			# make a factor with three levels:
			# 		wt,
			#		non-recurrent mutant
			# 		recurrent mutant
			# use for boxplot and  stripchart x-axis
			
			# start by setting all cell lines to wt
			wt_mut_grps_strings <- rep(
				"wt",
				times=length(mutations[,results$marker[i]])
				)
			
			# set the non-recurrent mutations
			wt_mut_grps_strings[which(exclusions[,results$marker[i]] == 1)] <- "non-rec. mut."
#print(wt_mut_grps_strings)
			# set the recurrent/functional mutations
			wt_mut_grps_strings[which(mutations[,results$marker[i]] == 1)] <- "rec. mut."
#print(wt_mut_grps_strings)
			wt_grp_rows <- which(wt_mut_grps_strings == "wt")
			nonfunc_mut_grp_rows <- which(wt_mut_grps_strings == "non-rec. mut.")
			func_mut_grp_rows <- which(wt_mut_grps_strings == "rec. mut.")
#print(wt_grp_rows)
#print(nonfunc_mut_grp_rows)
#print(func_mut_grp_rows)

##			png(filename=paste(
##				prefix_for_filename,
##				marker_gene,
##				"_",
##				target_gene,
##				"_",
##				suffix_for_filename,
##				"_",
##				"_PMID", pubmed_id_for_filename, ".png",
##				sep=""
##				),
				# width=5.3, height=4.5, units="in", res=96)
				# width=4.0, height=4.5, units="in", res=96)
##				width=4.0, height=4.0, units="in", res=96)
				# width=400, height=400) # default is pixils: , units="in"
				#  res = .... defaults to 72. The smaller this number, the larger the plot area in inches, and the smaller the text relative to the graph itself.
##			par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 0.1) ) # SJB: was: width=2.5, height=3, units="in", res=96
			#par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 1.4)) # <-- for legend at right.  SJB: original was: width=2.5, height=3
		
			# boxplot based on all data (wt and mut groups)
			# This print(...) just writes to the console - want to write to file - so maybe add to table then write.table(..
            #print(i)
            #print(zscores[wt_grp_rows,results$target[i]])
            #print(zscores[func_mut_grp_rows,results$target[i]])
#print("B")			
			boxplot(
				zscores[wt_grp_rows,results$target[i]],
				zscores[func_mut_grp_rows,results$target[i]],
				pch="",
#				sub=paste(marker_gene, "status"),
#				ylab=paste(target_gene, "z-score"),
				names=c("wt", "mutant"),
				cex.axis=1.5   # was 1.5
				)
			abline(
				-2,0,col="red",lty=2
				)
			# Draw the absline while xpdf=FALSE (changed to TRUE for legend), otherwise line draw accross whole image, instead of just accross the plots area.

			# Trim the target_variant last character from the gene names for Achilles data:
			if ((data_set == "Achilles") || (data_set == "Achilles_CRISPR")) {target_gene = substr(target_gene, 1, nchar(target_gene)-1)}
#print("C")
			# mtext() - write text onto the margins of a plot:
			# where: side is (1=bottom, 2=left, 3=top, 4=right).
			# line	= on which MARgin line, starting at 0 counting outwards.
			# cex= character expansion factor. NULL and NA are equivalent to 1.0. This is an absolute measure, not scaled by par("cex") or by setting par("mfrow") or par("mfcol"). Can be a vector.
			# SJB, changed line=2 to line=2.2 for horizontal axis text:
print(sprintf("driver:%s,target:%s",marker_gene,target_gene))

			mtext(paste(marker_gene, "status"), 1, line=2.3, cex=1.5)  # is horizontal axis text
			mtext(paste(target_gene, response_type), 2, line=2.3, cex=1.5)

			### remove last character .....substr(t, 1, nchar(t)-1)
			# or regexp: gsub(".$", "", c('01asap05a', '02ee04b')) 
#print("D")			
#			print(summary(wt_mut_grps))

			# Draw legend first, so plot points can be drawn over it x=0.45,y=-4.2
			# How to put legend outside plot area (setting xpd=TRUE to plot outside plot area, and using a negative inset): http://stackoverflow.com/questions/3932038/plot-a-legend-outside-of-the-plotting-area-in-base-graphics
			# (There are better methods on that webpage, eg:
			# Expand right side of clipping rect to make room for the legend:
            # oldpar <- par(xpd=T, mar=par()$mar+c(0,0,0,6)) # BUT using mai=....
            # Plot graph normally
            # plot(1:3, rnorm(3), pch = 1, lty = 1, type = "o", ylim=c(-2,2)) lines(1:3, rnorm(3), pch = 2, lty = 2, type="o")
            # Plot legend where you want
            # legend(3.2,1,c("group A", "group B"), pch = c(1,2), lty = c(1,2))
            # Restore default clipping rect
            # par(oldpar)
			# Not plotting legend as part of boxplot image now.
			# legend(xpd=TRUE, "topright", inset=c(-0.41,0), legend=tissue_pretty_names, fill=tissue_cols, cex=0.75 )  # was: x=1, y=1
			# legend("topleft", legend=c("Line 1", "Line 2"), col=c("red", "blue"), lty=1:2, cex=0.8)
			
			# points for each tissue type
			j <- NULL
			for(j in 1:length(tissue_actual_names)){
				tissue <- tissue_actual_names[j]
				wt_rows_by_tissue <- which(
					wt_mut_grps_strings == "wt" &
					tissues[,tissue] == 1
					)
				mutant_rows_by_tissue <- which(
					wt_mut_grps_strings == "rec. mut." &
					tissues[,tissue] == 1
					)
				
			    ### SJB: To get row names, use: print(row.names(tissues)[wt_rows_by_tissue])				
				if(length(wt_rows_by_tissue) > 0){
					# plot at 1
					# jitter(): https://stat.ethz.ch/R-manual/R-devel/library/base/html/jitter.html
					# on Uniform distribution: https://stat.ethz.ch/R-manual/R-devel/library/stats/html/Uniform.html
					# x <- jitter(rep(1,times=length(wt_rows_by_tissue)), amount=0.33)
					y <- zscores[wt_rows_by_tissue,results$target[i]]
					cell_lines = row.names(tissues)[wt_rows_by_tissue] # Added by SJB
					print(c(round(x,2),y,cell_lines)) # tissue_cols[j])) # Added by SJB
					for(k in 1:length(wt_rows_by_tissue)) {print(sprintf("x:%.2f,y:%.2f,c:%s",x[k],y[k],cell_lines[k]))}
					# or use: sprintf("%.3f", pi)
					points(
						x,
						y,
						col=tissue_cols[j],
						pch=19,
						cex=1.5
						)
				}
				if(length(mutant_rows_by_tissue) > 0){
					# plot at 2
					x <- jitter(rep(2,times=length(mutant_rows_by_tissue)), amount=0.33)
					y <- zscores[mutant_rows_by_tissue,results$target[i]]
					cell_lines = row.names(tissues)[wt_rows_by_tissue] # Added by SJB
					print(c(round(x,2),y,cell_lines,tissue_cols[j])) # Added by SJB
					for(k in 1:length(mutant_rows_by_tissue)) {print(sprintf("x:%.2f,y:%.2f,c:%s",x[k],y[k],cell_lines[k]))}
					points(
						x,
						y,
						col=tissue_cols[j],
						pch=19,
						cex=1.5
						)
				}
			}	
####			dev.off()
		}
	}
}



# Better to change this function so that it doesn't need tissue_actual_names list:

write_box_dot_plot_data <- function(
	results,
	zscores,
	mutation.classes,
	mutations,
	exclusions,
	tissues,
	fileConn,
	writeheader,
	tissue_actual_names,
	response_type="Z-score"
	){
	
#print(head(mutation.classes,n=2))
#print(head(zscores,n=2))
#print(head(mutations,n=2))


# Using cat() as does less conversion than print() so should be faster: https://stat.ethz.ch/R-manual/R-devel/library/base/html/cat.html
#fileConn<-file("boxplot_dataA_test.txt", open="w") # Output file. Needs "w" otherwise cat(...) overwrites previous cat()'s rather than appending. To open and append to existing file use "a"

if (writeheader){cat(names(results), "boxplot_data\n", file=fileConn, sep="\t")}
# The by_tissue results will have extra 'tissue' column.

	data_rows <- character(500) # Initialise to a large empty vector so that appending is fast
	
	i <- NULL	
	for(i in 1:nrow(results)){
# SJB commented out the following test, as the new effect_size (CLES) function does not output this "med.grpA.med.grpB" result:
#		if(is.na(results$med.grpA.med.grpB[i])){
#			next
#		}

# Substitutions for removing the tissue name from the cell_line, and checking it is valid.
# test="AAA_JJJ_UUUU_OOPPO"
# sub("_.*$","",test)
# [1] "AAA"
# sub("^(.*?)_","",test) # "?" for non-greedy
# [1] "JJJ_UUUU_OOPPO"

#if (i>10){ # For testing.
  #cat("}\n",  file=fileConn, append=TRUE)
  #close(fileConn)
  #stop("Finished")
  #}

		if(results$nA[i] > 2){
			marker_gene <- strsplit(results$marker[i], "_")[[1]][1]
			target_gene <- strsplit(results$target[i], "_")[[1]][1]
			
			# make a factor with three levels:
			# 		wt,
			#		non-recurrent mutant
			# 		recurrent mutant
			# use for boxplot and  stripchart x-axis
			
			# start by setting all cell lines to wt
			wt_mut_grps_strings <- rep(
				"wt",
				times=length(mutations[,results$marker[i]])
				)
			
			# set the non-recurrent mutations
			wt_mut_grps_strings[which(exclusions[,results$marker[i]] == 1)] <- "non-rec. mut."
#print(wt_mut_grps_strings)
			# set the recurrent/functional mutations
			wt_mut_grps_strings[which(mutations[,results$marker[i]] == 1)] <- "rec. mut."						
#print(wt_mut_grps_strings)
			wt_grp_rows <- which(wt_mut_grps_strings == "wt")
			nonfunc_mut_grp_rows <- which(wt_mut_grps_strings == "non-rec. mut.")
			func_mut_grp_rows <- which(wt_mut_grps_strings == "rec. mut.")
#print(wt_grp_rows)
#print(nonfunc_mut_grp_rows)
#print(func_mut_grp_rows)

##			png(filename=paste(
##				prefix_for_filename,
##				marker_gene,
##				"_",
##				target_gene,
##				"_",
##				suffix_for_filename,
##				"_",
##				"_PMID", pubmed_id_for_filename, ".png",
##				sep=""
##				),
				# width=5.3, height=4.5, units="in", res=96)
				# width=4.0, height=4.5, units="in", res=96)
##				width=4.0, height=4.0, units="in", res=96)
				# width=400, height=400) # default is pixils: , units="in"
				#  res = .... defaults to 72. The smaller this number, the larger the plot area in inches, and the smaller the text relative to the graph itself.
##			par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 0.1) ) # SJB: was: width=2.5, height=3, units="in", res=96
			#par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 1.4)) # <-- for legend at right.  SJB: original was: width=2.5, height=3

			# Trim the target_variant last character from the gene names for Achilles data:
			if ((data_set == "Achilles") || (data_set == "Achilles_CRISPR")) {target_gene = substr(target_gene, 1, nchar(target_gene)-1)}
#print(sprintf("driver:%s,target:%s",marker_gene,target_gene), quote = FALSE)

			
			# boxplot based on all data (wt and mut groups)
			# This print(...) just writes to the console - want to write to file - so maybe add to table then write.table(..
            #print(i)
            #print(zscores[wt_grp_rows,results$target[i]])
            #print(zscores[func_mut_grp_rows,results$target[i]])
#print("B")			
# SJB: "In a box and whisker plot, a box is drawn around the quartile values, and the whiskers extend from each quartile to the extreme data points.
# http://intermath.coe.uga.edu/dictnary/descript.asp?termID=57

#Box Plots: http://sphweb.bumc.bu.edu/otlt/MPH-Modules/BS/R/R2_SummaryStats-Graphs/R2_SummaryStats-Graphs_print.html
# A "boxplot", or "box-and-whiskers plot" is a graphical summary of a distribution; the box in the middle indicates "hinges" (close to the first and third quartiles) and median. The lines ("whiskers") show the largest or smallest observation that falls within a distance of 1.5 times the box size from the nearest hinge. If any observations fall farther away, the additional points are considered "extreme" values and are shown separately. A boxplot can often give a good idea of the data distribution, and is often more useful to compare distributions side-by-side, as it is more compact than a histogram. We will see an example soon.

# From: https://stat.ethz.ch/R-manual/R-devel/library/grDevices/html/boxplot.stats.html
#  boxplot.stats(x, coef = 1.5, do.conf = TRUE, do.out = TRUE)

#print("wt:")
#				print(zscores[wt_grp_rows,results$target[i]])
#wt_quart = quantile(zscores[wt_grp_rows,results$target[i]]) # Gives: Min, 1st Quartile, Median, 3rd Quartile, Max
#print(wt_quart)

wt_boxplot = boxplot.stats( round(zscores[wt_grp_rows,results$target[i]],2), do.conf = FALSE, do.out = TRUE )
 # The round is so that will get same results as my javascript boxplot_stats() which uses input y values already rounded to 2 decimal places.
wt_boxplot_stats = wt_boxplot$stats


#wt_boxplot_outliers = wt_boxplot$out # ie. points outside the 1.5 of the boxplot limits

#print(wt_boxplot)
#print("mutant:")
#				print(zscores[func_mut_grp_rows,results$target[i]])
#mutant_quart = quantile(zscores[func_mut_grp_rows,results$target[i]])
#print(mutant_quart)

# http://r.789695.n4.nabble.com/Whiskers-on-the-default-boxplot-graphics-td2195503.html
# http://stackoverflow.com/questions/8844845/how-do-i-turn-the-numeric-output-of-boxplot-with-plot-false-into-something-usa
# http://rstudio-pubs-static.s3.amazonaws.com/21508_35a770dc38fa4658accef1acc4fb2fbe.html
# *** GOOD: http://www.sr.bham.ac.uk/~ajrs/R/r-show_data.html
# boxplot.stats: https://stat.ethz.ch/R-manual/R-devel/library/grDevices/html/boxplot.stats.html
mutant_boxplot = boxplot.stats( round(zscores[func_mut_grp_rows,results$target[i]],2), do.conf = FALSE, do.out = TRUE )
 # The round is so that will get same results as my javascript boxplot_stats() which uses input y values already rounded to 2 decimal places.
mutant_boxplot_stats = mutant_boxplot$stats
#mutant_boxplot_outliers = mutant_boxplot$out

# add min and max ...... floor and ceiling integers for graph Y axis size.....

#boxplot_min <- min(wt_boxplot_outliers, mutant_boxplot_outliers, mutant_boxplot_stats[1], wt_boxplot_stats[1])
#boxplot_max <- max(wt_boxplot_outliers, mutant_boxplot_outliers, mutant_boxplot_stats[5], wt_boxplot_stats[5])

# or simpler to just do: 
#boxplot_min <- min()
# boxplot_range <- range(zscores[wt_grp_rows,results$target[i]], zscores[func_mut_grp_rows,results$target[i]])
boxplot_range <- range(wt_boxplot_stats, wt_boxplot$out, mutant_boxplot_stats, mutant_boxplot$out)
boxplot_range <- c( floor(boxplot_range[1]), ceiling(boxplot_range[2]) ) # Round lower down and upper up to integers.
#also:
#write.csv(sales.data, "SalesData.csv", row.names = FALSE)
#and
#write.table(.....)

#write(): https://stat.ethz.ch/R-manual/R-devel/library/base/html/write.html
#and:
#writeLines() http://stackoverflow.com/questions/2470248/write-lines-of-text-to-a-file-in-r
#sink() https://stat.ethz.ch/R-manual/R-devel/library/base/html/sink.html


#* Breakpoints in RStudio: http://stackoverflow.com/questions/7486386/how-to-step-through-an-r-script-from-the-begining

#print(mutant_boxplot)

#			boxplot(
#				zscores[wt_grp_rows,results$target[i]],
#				zscores[func_mut_grp_rows,results$target[i]],
#				pch="",
#				sub=paste(marker_gene, "status"),
#				ylab=paste(target_gene, "z-score"),
#				names=c("wt", "mutant")
#				cex.axis=1.5   # was 1.5
#				)
#			abline(
#				-2,0,col="red",lty=2
#				)
#for (l in 1:length(wt_boxplot_stats)){abline(wt_boxplot_stats[l],0,col="green",lty=2)}
#for (l in 1:length(mutant_boxplot_stats)){abline(mutant_boxplot_stats[l],0,col="blue",lty=2)}


			# Draw the absline while xpdf=FALSE (changed to TRUE for legend), otherwise line draw accross whole image, instead of just accross the plots area.

#print("C")
			# mtext() - write text onto the margins of a plot:
			# where: side is (1=bottom, 2=left, 3=top, 4=right).
			# line	= on which MARgin line, starting at 0 counting outwards.
			# cex= character expansion factor. NULL and NA are equivalent to 1.0. This is an absolute measure, not scaled by par("cex") or by setting par("mfrow") or par("mfcol"). Can be a vector.
			# SJB, changed line=2 to line=2.2 for horizontal axis text:

##			mtext(paste(marker_gene, "status"), 1, line=2.3, cex=1.5)  # is horizontal axis text
##			mtext(paste(target_gene, response_type), 2, line=2.3, cex=1.5)

			### remove last character .....substr(t, 1, nchar(t)-1)
			# or regexp: gsub(".$", "", c("01asap05a", "02ee04b")) 
#print("D")			
#			print(summary(wt_mut_grps))

			# Draw legend first, so plot points can be drawn over it x=0.45,y=-4.2
			# How to put legend outside plot area (setting xpd=TRUE to plot outside plot area, and using a negative inset): http://stackoverflow.com/questions/3932038/plot-a-legend-outside-of-the-plotting-area-in-base-graphics
			# (There are better methods on that webpage, eg:
			# Expand right side of clipping rect to make room for the legend:
            # oldpar <- par(xpd=T, mar=par()$mar+c(0,0,0,6)) # BUT using mai=....
            # Plot graph normally
            # plot(1:3, rnorm(3), pch = 1, lty = 1, type = "o", ylim=c(-2,2)) lines(1:3, rnorm(3), pch = 2, lty = 2, type="o")
            # Plot legend where you want
            # legend(3.2,1,c("group A", "group B"), pch = c(1,2), lty = c(1,2))
            # Restore default clipping rect
            # par(oldpar)
			# Not plotting legend as part of boxplot image now.
			# legend(xpd=TRUE, "topright", inset=c(-0.41,0), legend=tissue_pretty_names, fill=tissue_cols, cex=0.75 )  # was: x=1, y=1
			# legend("topleft", legend=c("Line 1", "Line 2"), col=c("red", "blue"), lty=1:2, cex=0.8)
			
			# points for each tissue type

# Maybe append function.
# Maybe lapply(): http://www.r-bloggers.com/efficient-accumulation-in-r/
# http://www.win-vector.com/blog/2015/07/efficient-accumulation-in-r/

cell_line_count <- 0  # This should be same as the data_rows_count

data_rows_count <- 0  # Index for the 'data_rows' vector, which is number of cell-lines for this tissue (which is different from cell_line_count above for all the tissues for this driver+target)


# fill = FALSE, labels = NULL,
#    append = FALSE)
							
			j <- NULL
			for(j in 1:length(tissue_actual_names)){
				tissue <- tissue_actual_names[j]
# print(tissue)	
				wt_rows_by_tissue <- which(
					wt_mut_grps_strings == "wt" &
					tissues[,tissue] == 1
					)
				mutant_rows_by_tissue <- which(
					wt_mut_grps_strings == "rec. mut." &
					tissues[,tissue] == 1
					)

				# count to check that the full number of cell_lines is sent by the AJAX call:
                cell_line_count <- cell_line_count + length(wt_rows_by_tissue) + length(mutant_rows_by_tissue)
				
				# or set the data_rows vector length to the above: length(wt_rows_by_tissue) + length(mutant_rows_by_tissue)
				
			    ### SJB: To get row names, use: print(row.names(tissues)[wt_rows_by_tissue])				
				if(length(wt_rows_by_tissue) > 0){
					# plot at 1
					# jitter(): https://stat.ethz.ch/R-manual/R-devel/library/base/html/jitter.html
					#x <- jitter(rep(1,times=length(wt_rows_by_tissue)), amount=0.33)
					y <- zscores[wt_rows_by_tissue,results$target[i]]
					cell_lines <- row.names(tissues)[wt_rows_by_tissue] # Added by SJB

mutant_types <- mutation.classes[wt_rows_by_tissue,results$marker[i]] # Added by SJB - should all be 0 for wt.

					cell_line_tissues <- sub("^(.*?)_","",cell_lines) # the part after the first "_"
#					print(cell_line_tissues)
					if(length(which(cell_line_tissues != tissue)) > 0){
					   unequal_tissues <- which(cell_line_tissues != tissue)
					   for (k in 1:length(unequal_tissues)) {
					      if (tissue=="INTESTINE" && (cell_line_tissues[k]=="LARGE_INTESTINE" || cell_line_tissues[k]=="SMALL_INTESTINE")) {
						    #print(paste("Accepting:",cell_line_tissues[k],"==",tissue))
						    } else {
					         stop(paste("ERROR:",cell_line_tissues[k], "!=", tissue[k]))
						    }
					   # But for Achilles data we allow the case of: 
					   #LARGE_INTESTINE != INTESTINE
					   #SMALL_INTESTINE != INTESTINE
					   # and lung.
					   }
					}
					
					# for JSON:
					cell_line_names <- sub("_.*$","",cell_lines) # the part before the first "_"
					
					# eg: length(which(cle!="BONE")) >0 

# sub("_.*$","",test)
# [1] "AAA"
# sub("^(.*?)_","",test) # "?" for non-greedy
# [1] "JJJ_UUUU_OOPPO"
					
					#print(c(round(x,2),y,cell_line_names)) # tissue_cols[j])) # Added by SJB
					#for(k in 1:length(wt_rows_by_tissue)) {print(sprintf("x:%.2f,y:%.2f,c:%s",x[k],y[k],cell_line_names[k]), quote = FALSE)}
#writeLines(c(paste(marker_gene,target_gene)), fileConn)

# As JSON:
#cat(',"wt_',tissue,'":{', '"x":',toJSON(round(x,2)), ',"y":', toJSON(y), ',"c":',toJSON(cell_line_names),'}', file=fileConn, sep = "", append=TRUE)

# or as CSV:
for (k in 1:length(wt_rows_by_tissue)) {
  # cat(tissue,cell_line_names[k],y[k],"0;", file=fileConn, sep = ",") # "1" for mutant. (0 for wild type) Semi-colon is our end-of-line marker, instead of new-line.
  # cat(tissue,cell_line_names[k],round(x[k],2),y[k],"0;", file=fileConn, sep = ",") # "1" for mutant. (0 for wild type) Semi-colon is our end-of-line marker, instead of new-line.
  data_rows_count <- data_rows_count +1
  # Optionally add: (if (k==1) tissue else "")
  # The round(y[k],2) is needed for Achilles and Colt data, but seems already rounded in Campbell data:
  
  if (mutant_types[k]!=0) {stop(paste("ERROR: for k=",k,", mutant_types[k]=",mutant_types[k], "!= 0"))}
  data_rows[data_rows_count] <- paste(tissue,cell_line_names[k],round(y[k],2),"0", sep=",") # removed the semi colon, as will join at end using sep=';' as don't want semi-colon at end of the very last row.
  }
#  paste(tissue,cell_line_names,y,"0", sep=",", ';') # Maybe collapse argument will combine these together more efficiently than the above loop?

  
# fill = FALSE, labels = NULL,
#    append = FALSE)
				
					
					# or use: sprintf("%.3f", pi)
##					points(
##						x,
##						y,
##						col=tissue_cols[j],
##						pch=19,
##						cex=1.5
##						)
				}
				if(length(mutant_rows_by_tissue) > 0){
					# plot at 2
					#x <- jitter(rep(2,times=length(mutant_rows_by_tissue)), amount=0.33)
					y <- zscores[mutant_rows_by_tissue,results$target[i]]
mutant_types <- mutation.classes[mutant_rows_by_tissue,results$marker[i]] # Added by SJB - should be non-zeros.
					cell_lines <- row.names(tissues)[mutant_rows_by_tissue] # Added by SJB
					#print(c(round(x,2),y,cell_lines)) # ,tissue_cols[j] # Added by SJB
					#for(k in 1:length(mutant_rows_by_tissue)) {print(sprintf("x:%.2f,y:%.2f,c:%s",x[k],y[k],cell_lines[k]), quote = FALSE)}
					cell_line_tissues <- sub("^(.*?)_","",cell_lines) # the part after the first "_"
#					print(cell_line_tissues)
					if(length(which(cell_line_tissues != tissue)) > 0){
					   unequal_tissues <- which(cell_line_tissues != tissue)					
					   for (k in 1:length(unequal_tissues)) {
					      if (tissue=="INTESTINE" && (cell_line_tissues[k]=="LARGE_INTESTINE" || cell_line_tissues[k]=="SMALL_INTESTINE")) {
						    # print(paste("Accepting:",cell_line_tissues[k],"==",tissue))
						    } else {
					         stop(paste("ERROR:",cell_line_tissues[k], "!=", tissue[k]))
						    }
						}
					}
					# for JSON:
					cell_line_names <- sub("_.*$","",cell_lines) # the part before the first "_"					
#cat("mutant",tissue,round(x,2),y,cell_line_names, file=fileConn, sep = "\t", append=TRUE)

#cat('"',tissue,'":{', file=fileConn, sep = "", append=TRUE)
#if(need_comma){cat(",", file=fileConn, sep = "", append=TRUE); need_comma<-FALSE}
#cat(',"mu":{', '"x":',toJSON(round(x,2)), ',"y":', toJSON(y), ',"c":',toJSON(cell_line_names),'}', file=fileConn, sep = "", append=TRUE)


# As JSON:
#cat(',"mu_',tissue,'":{', '"x":',toJSON(round(x,2)), ',"y":', toJSON(y), ',"c":',toJSON(cell_line_names),'}', file=fileConn, sep = "", append=TRUE)
# or could output cell_lines more compactly as list one string, instead of array: 
# "c":["143B","CAL72","HOS","HUO3N1","HUO9","MG63","NOS1","NY","SAOS2","SJSA1","U2OS"]
# "c":"143B,CAL72,HOS,HUO3N1,HUO9,MG63,NOS1,NY,SAOS2,SJSA1,U2OS"
	
	
#	http://stackoverflow.com/questions/2436688/append-an-object-to-a-list-in-r-in-amortized-constant-time-o1
# a <- list(0)
#            for(i in 1:n) {a <- list(a, list(i))}
			

	
# or as CSV:
for (k in 1:length(mutant_rows_by_tissue)) {
  #cat(tissue,cell_line_names[k],y[k],"1;", file=fileConn, sep = ",")# "1" for mutant. (0 for wild type) Semi-colon is our end-of-line marker, instead of new-line.
  #cat(tissue,cell_line_names[k],round(x[k],2),y[k],"1;", file=fileConn, sep = ",")# "1" for mutant. (0 for wild type) Semi-colon is our end-of-line marker, instead of new-line.
  data_rows_count <- data_rows_count +1
  # Optionally add:  (if (length(wt_rows_by_tissue)==0 && k==1) tissue else "")
  # The round(y[k],2) is needed for Achilles and Colt data, but seems already rounded in Campbell data.  
  if (mutant_types[k]<=0) {stop(paste("ERROR: for k=",k,", mutant_types[k]=",mutant_types[k], "<= 0"))}
  data_rows[data_rows_count] <- paste(tissue,cell_line_names[k],round(y[k],2),mutant_types[k], sep=",") # removed ';' from end.
  # or: ifelse(k==1, tissue, "")
  
  # for empty first tissue use: if k==1 ""
  # if pre-allocate rows to be large vector then keep a counter might be faster..., do not need to empty, just take slice upto size.

#  eg:
#  res <- 
# There exists also the function ifelse that allows rewriting the expression above as:


  } # end of: for (k in 1:length(mutant_rows_by_tissue)) { ....

##					points(
##						x,
##						y,
##						col=tissue_cols[j],
##						pch=19,
##						cex=1.5
##						)
				}  # end of: if(length(mutant_rows_by_tissue) > 0){ ....
#=======================================  

#writeLines(c(paste(marker_gene,target_gene)), fileConn)



# As JSON:
# cat("\t{",'"range":',toJSON(boxplot_range), ',"wt_box":',toJSON(wt_boxplot_stats), ',"mu_box":',toJSON(mutant_boxplot_stats), file=fileConn, sep = "", append=TRUE)

# or as CSV:
#cat("\t",boxplot_range, wt_boxplot_stats, mutant_boxplot_stats, file=fileConn, sep = "", append=TRUE)

#cat("\t", file=fileConn)
#cat("range",boxplot_range, file=fileConn, sep = ",")
#cat(";", file=fileConn)
#cat("wt_box",wt_boxplot_stats, file=fileConn, sep = ",")
#cat(";", file=fileConn)
#cat("mu_box",mutant_boxplot_stats, file=fileConn, sep = ",")

#=================================
			} # end of: for(j in 1:length(tissue_actual_names)){ ....
#cat(unname(unlist(results[i,])),file=fileConn,sep="\t")
#cat("\t", file=fileConn)
#cat(cell_line_count, boxplot_range, wt_boxplot_stats, mutant_boxplot_stats, file=fileConn, sep = ",")
#cat(";", file=fileConn)
#cat(head(data_rows, n = data_rows_count), file=fileConn, sep=';')

# or as one cat():

# Write the full results (ie. driver,target,wilcox_p, CLES, etc. As is a connection don't need "append=TRUE"
# Hierarchy of separaters: , ; \t \n
#  output the cell_line_count at start and put box plot stats on one line

if (data_rows_count!=cell_line_count) {stop(paste("ERROR:",cell_line_count, "!=", tissue))}
# Correct:
#"ERBB2_2064_ENSG00000141736      MAP2K3_ENSG00000034152  12      67      0.000379762881197737    0.807213930348259       range,-5,2;
#wt_box,-2.66,-1.28,-0.62,0.04,1.26;
#mu_box,-4.61,-3.555,-1.765,-0.91,-0.62;
#BONE,143B,1.14,-0.21,0;BONE,CAL72,1.1,-0.61,0;BONE,G292,1.01,-1.85,0;BONE,HOS,1.13,-2.15,0;BONE,HUO3N1,0.86,-1.12,0;BONE,HUO9,0.82,-0.91,0;BONE,MG63,0.71,-1.48,0;BONE,NOS1,1.12,-0.99,0;BONE,NY,0.97,0.18,0;BONE,SAOS2,1.16,-0.91,0;BONE,SJSA1,1.11,0.88,0;BONE,U2O"

"ERBB2_2064_ENSG00000141736      MAP2K3_ENSG00000034152  12      67      0.000379762881197737    0.807213930348259       -1.765  -0.62   -1.145  
(count:)79,
(range:)-5,2,
(wt_box:)-2.66,-1.28,-0.62,0.04,1.26,
(mu_box:)-4.61,-3.555,-1.765,-0.91,-0.62;
(cell_line:)BONE,143B,-0.21,0;
(cell_line:)BONE,CAL72,-0.61,0;
(cell_line:)BONE,G292,-1.85,0;BONE,HOS,-2.15,0;BONE,HUO3N1,-1.12,0;BONE,HUO9,-0.91,0;BONE,MG63,-1.48,0;BONE,NOS1,-0.99,0;BONE,NY,0.18,0;BONE,SAOS2,-0.91,0;BONE,SJSA1,0.88,0;BONE,U2OS,0.36,0;BREAST,BT20,-2.29,0;BREAST,BT549,-1.67,0;BREAST,CAL120,1.26,0;BREAST,CAL51,-0.67,0;BREAST,CAMA1,1.04,0;BREAST,DU4475,0.22,0;BREAST,HCC38,-0.23,0;BREAST,HCC70,-0.91,0;BREAST,HS578T,-2.03,0;BREAST,MCF7,-0.42,0;BREAST,MDAMB157,-1.54,0;BREAST,MDAMB231,-0.1,0;..."

cat(file=fileConn, sep="\t", unname(unlist(results[i,])))
cat(file=fileConn, "\t")
cat(file=fileConn, sep = ",", cell_line_count, boxplot_range, wt_boxplot_stats, mutant_boxplot_stats)
cat(file=fileConn, ";")
cat(file=fileConn, sep=';', data_rows[1:data_rows_count])  # data_rows[1:data_rows_count] is same as head(data_rows, n=data_rows_count)
cat(file=fileConn, "\n")

####			dev.off()
# as JSON:
# cat("}\n",  file=fileConn, append=TRUE)
# as CSV:
#cat("count",cell_line_count, file=fileConn, sep = ",")
# cat("count", cell_line_count, file=fileConn, sep = ",")


		} # end of: if(results$nA[i] > 2){ marker_gene <- strsplit(results$marker[i], "_")[[1]][1]; target_gene <- strsplit(results$target[i], "_")[[1]][1]
	}
#	close(fileConn) # caller should close the fileConn
}



'
# Old test:
OLD_run_univariate_tests <- function(
	zscores,
	mutations,
	all_variants,
	sensitivity_thresholds=NULL,
	nperms=1000000,
	alt="less"
	){
	
	
	zscores <- as.matrix(zscores)
	mutations <- as.matrix(mutations)
	all_variants <- as.matrix(all_variants)
	
	
	results <- NULL
	i <- NULL
	for(i in seq(1:length(colnames(mutations)))){
		
		print(paste("working on:", colnames(mutations)[i]))
		
		grpA <- which(mutations[,i] > 0)
		
		#gene <- strsplit(
		#	colnames(mutations)[i],
		#	"_"
		#	)[[1]][1]
		gene <- colnames(mutations)[i]
		
		
		# grpB includes cell lines with no reported mutations at all
		# in gene...
		grpB <- which(all_variants[,gene] == 0)
		
		# skip if nA < 3 as we are never going to
		# consider anything based on n=2
		if(length(grpA) < 3 | length(grpB) < 3){
			next
		}
		

# this code changed because it does not exclude
# uncertain observations
#		# this is used for spearman correlation...
#		mut.status <- rep(0,nrow(zscores))
#		mut.status[which(mutations[,i] > 0)] <- 1

		# this is used for spearman correlation...
		mut.status <- rep(NA,nrow(zscores))
		mut.status[which(mutations[,i] == 1)] <- 1
		mut.status[which(all_variants [,i] == 0)] <- 0

		
		j <- NULL
		for(j in seq(1:length(colnames(zscores)))){
			
						
			# skip if we have no viability measurements
			# in one or other group
			if(length(na.omit(zscores[grpA,j])) < 3){
				next
			}
			if(length(na.omit(zscores[grpB,j])) < 3){
				next
			}
			
			# calc the median permutation test p-value
			real.med.diff <- median(na.omit(zscores[grpA,j])) - median(na.omit(zscores[grpB,j]))
			
			# permute the groups nperms times, sampling with group sizes equal to grpA
			sample.size <- length(grpA)

			mpt.pval <- "NA"

# begin uncommenting code for MPTest

			k <- NULL
			permuted.med.diffs <- NULL
			grpAB <- c(grpA,grpB) # join up the actual cell lines we used so we can sample them.

			for(k in 1:1000){
				index <- sample(1:length(grpAB), size=sample.size, replace=FALSE)
				permuted.grpA <- grpAB[index]
				permuted.grpB <- grpAB[-index]
				permuted.med.diffs[k] <- median(na.omit(zscores[permuted.grpA,j]))-median(na.omit(zscores[permuted.grpB,j]))
			}
			mpt.pval <- length(which(permuted.med.diffs <= real.med.diff)) / 1000		

			if(mpt.pval < 0.010){
				for(k in 1001:10000){
					index <- sample(1:length(grpAB), size=sample.size, replace=FALSE)
					permuted.grpA <- grpAB[index]
					permuted.grpB <- grpAB[-index]
					permuted.med.diffs[k] <- median(na.omit(zscores[permuted.grpA,j]))-median(na.omit(zscores[permuted.grpB,j]))
				}
				mpt.pval <- length(which(permuted.med.diffs <= real.med.diff)) / 10000
			}

			if(mpt.pval < 0.0010){
				for(k in 10001:100000){
					index <- sample(1:length(grpAB), size=sample.size, replace=FALSE)
					permuted.grpA <- grpAB[index]
					permuted.grpB <- grpAB[-index]
					permuted.med.diffs[k] <- median(na.omit(zscores[permuted.grpA,j]))-median(na.omit(zscores[permuted.grpB,j]))
				}
				mpt.pval <- length(which(permuted.med.diffs <= real.med.diff)) / 100000
			}

			if(mpt.pval < 0.00010){
				for(k in 100001:1000000){
					index <- sample(1:length(grpAB), size=sample.size, replace=FALSE)
					permuted.grpA <- grpAB[index]
					permuted.grpB <- grpAB[-index]
					permuted.med.diffs[k] <- median(na.omit(zscores[permuted.grpA,j]))-median(na.omit(zscores[permuted.grpB,j]))
				}
				mpt.pval <- length(which(permuted.med.diffs <= real.med.diff)) / 1000000
			}

# end uncommenting code for MPTest
			
			wilcox.p <- NA
			try(
				test <- wilcox.test(
					zscores[grpA,j],
					zscores[grpB,j],
					alternative=alt
				)
			)
			wilcox.p <- test$p.value
			
			# get the Spearman r value as an effect size estimate
			spearman <- NULL
			try(
				spearman <- cor.test(zscores[,j], mut.status, method="spearman", use="complete.obs", alternative=alt)
			)
			
			this_threshold <- 0
			if(!is.null(sensitivity_thresholds)){
				this_threshold <- sensitivity_thresholds[colnames(zscores)[j]]
			}
			
			med.grpA <- median(zscores[grpA,j], na.rm=TRUE)
			med.grpB <- median(zscores[grpB,j], na.rm=TRUE)
			mad.grpA <- mad(zscores[grpA,j], na.rm=TRUE)
			mad.grpB <- mad(zscores[grpB,j], na.rm=TRUE)
			countA.sens <- length(which(zscores[grpA,j] <= this_threshold))
			countB.sens <- length(which(zscores[grpB,j] <= this_threshold))
#			countA.sens <- length(which(zscores[grpA,j] <= sensitivity_thresholds[colnames(zscores)[j]]))
#			countB.sens <- length(which(zscores[grpB,j] <= sensitivity_thresholds[colnames(zscores)[j]]))
			med.diff <- med.grpA - med.grpB
			marker <- colnames(mutations)[i]
			target <- colnames(zscores)[j]
			nA <- length(grpA)
			nB <- length(grpB)
			nMin <- min(nA, nB)
			pcnt.grpA.sens <- 100 * countA.sens / nA
			pcnt.grpB.sens <- 100 * countB.sens / nB
			min.grpA <- min(zscores[grpA,j], na.rm=TRUE)
			min.grpB <- min(zscores[grpB,j], na.rm=TRUE)
			spearman.r <- spearman$estimate
			spearman.p <- spearman$p.value
			
			# Output the result if min sample size is 2 or more
			if(nMin > 1){
				results <- rbind(
					results,
					c(
						marker,
						target,
						nA,
						nB,
						this_threshold,
						med.grpA,
						med.grpB,
						med.diff,
						countA.sens,
						countB.sens,
						pcnt.grpA.sens,
						pcnt.grpB.sens,
						min.grpA,
						min.grpB,
						spearman.r,
						spearman.p,
						wilcox.p,
						mpt.pval
					)
				)
			}
		}
	}
	
	if(is.null(nrow(results))){
		return(NULL)
	}
	
	colnames(results) <- c(
		"marker",
		"target",
		"nA",
		"nB",
		"sensitive.threshold",
		"med.grpA",
		"med.grpB",
		"med.grpA-med.grpB",
		"count.grpA.sens",
		"count.grpB.sens",
		"percent.grpA.sens",
		"percent.grpB.sens",
		"min.grpA",
		"min.grpB",
		"spearman.r",
		"spearman.p",
		"wilcox.p",
		"mptest.p"
	)
	
	return(results)
	
} # end run_univariate_tests
'







