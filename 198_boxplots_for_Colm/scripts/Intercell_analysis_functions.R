# ====================================== #
# Analysis functions used for univariate
# analyses in the Intercell II work
# jamesc@icr.ac.uk, 11th March 2014
# ====================================== #


require("preprocessCore")
require(gplots)
require(mixtools)

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


icrpal <- palette(c("#C9DD03", "#FFD602", "#F9A100", "#EE7EA6", "#A71930", "#CCCCCC","#726E20" , "#6E273D", "#F00034", "#ADAFAF", "#003D4C"))

# SJB - Achilles:
# "HEADNECK" "CERVICAL" are not in Achilles - so need to comment them out below as mini_boxplot uses legend_actual_tissues
# Added for Achilles: HAEMATOPOIETIC_AND_LYMPHOID_TISSUE, INTESTINE, KIDNEY, LIVER, PROSTATE, SKIN, SOFT_TISSUE, STOMACH, URINARY_TRACT
# Achilles - Numbers of celllines for each tissue type: BONE=6,  BREAST=12, CENTRAL_NERVOUS_SYSTEM=34, ENDOMETRIUM=2, HAEMATOPOIETIC_AND_LYMPHOID_TISSUE=30, INTESTINE=21, KIDNEY=10, LIVER=1, LUNG=23, OESOPHAGUS=10, OVARY=29, PANCREAS=17, PROSTATE=3, SKIN=7, SOFT_TISSUE=2, STOMACH=4, URINARY_TRACT=3
	
if (isAchilles) {
  legend_pretty_tissues = c(
	"Osteosarcoma",
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
	"Intestine",
	"Kidney",
	"Liver",
	"Prostate",
	"Skin",
	"Soft tissue",
	"Stomach",
	"Urinary tract"
	)	
} else if(isCampbell) {	
  legend_pretty_tissues = c(
	"Osteosarcoma",
	"Breast",
	"Lung",
	"Head & Neck",
	"Pancreas",
	"Cervical",
	"Ovary",
	"Esophagus",
	"Endometrium",
	"CNS"
	)
} else if(isColt) {	 # Only Breast
  legend_pretty_tissues = c(
	"Breast"
	)
}

if (isAchilles) {
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
	"INTESTINE",
	"KIDNEY",
	"LIVER",
	"PROSTATE",
	"SKIN",
	"SOFT_TISSUE",
	"STOMACH",
	"URINARY_TRACT"
	)
} else if (isCampbell) {
  legend_actual_tissues = c(
	"BONE",
	"BREAST",
	"LUNG",
	"HEADNECK",
	"PANCREAS",
	"CERVICAL",
	"OVARY",
	"OESOPHAGUS",
	"ENDOMETRIUM",
	"CENTRAL_NERVOUS_SYSTEM"
	)
} else if(isColt) {	 # Only Breast
  legend_actual_tissues = c(
	"BREAST"
    )
}

if (isAchilles) {
  legend_col=c(
	"yellow",
	"deeppink",
	"darkgrey",
#	"firebrick4",
	"purple",
#	"blue",
	"cadetblue",
	"green",
	"orange",
	"darkgoldenrod4",
	"darkred",
    "saddlebrown",
	"indianred",
	"slategray",
	"turquoise",
	"peachpuff",
	"lightgrey",
    "black",
    "yellowgreen"
	)
} else if (isCampbell) {	
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
} else if (isColt) {
  legend_col=c(
	"deeppink"
    )
}

	
names(legend_col) <- legend_actual_tissues

# SJB - list copied from the "run_intercell_analysis.R" downloaded from github GeneFunctionTeam repo on 12 March 2016
# Define the set of 21 genes with
# good represention (≥ 7 mutants).
# This list can be used to filter
# the complete set of tests
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
	"NOTCH2_4853_ENSG00000134250",
	"NRAS_4893_ENSG00000213281",
	"PIK3CA_5290_ENSG00000121879",
	"PTEN_5728_ENSG00000171862",
	"RB1_5925_ENSG00000139687",
	"MAP2K4_6416_ENSG00000065559",
	"SMARCA4_6597_ENSG00000127616",
	"STK11_6794_ENSG00000118046",
	"TP53_7157_ENSG00000141510",
	"ARID1A_8289_ENSG00000117713",
	"FBXW7_55294_ENSG00000109670"
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

# This is the revised code from Colm (17 Mar 2016) which include the effect size test, and without spearman, etc:
run_univariate_tests <- function(
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

#       Skip if driver mutation is NOT in the above list of 21 genes for the Achilles data	
#       Added by SJB to speed up initialy analysis of Achilles data by focusing in the 21 genes.
#	    if ( !(colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
#       Skip if driver mutation IS in the above list of 21 genes - as they are already processed.
	    #if ( (colnames(mutations)[i] %in% cgc_vogel_genes_with_n7) ) {
		#	print(paste("skipping:", colnames(mutations)[i]))
		#	next
		#}

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
	#	print("C")
		cellline_count <- sum(
			x$tissues[,tissue]
			)
	#	print("D")
		if(cellline_count < 5){
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
			sensitivity_thresholds=x$rnai_iqr_thresholds
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

	png(filename=paste("Legend_PMID", pubmed_id, ".png", sep=""),
		# width=5.3, height=4.5, units="in", res=96)
		# width=4.0, height=4.5, units="in", res=96)
		width=1.5, height=4.0, units="in", res=96)
		# width=400, height=400) # default is pixils: , units="in"
		#  res = .... defaults to 72. The smaller this number, the larger the plot area in inches, and the smaller the text relative to the graph itself.

	par(bty="n", mai=c(0.1, 0.1, 0.1, 0.1) ) # SJB: was: width=2.5, height=3, units="in", res=96
	#par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 1.4)) # <-- for legend at right.  SJB: original was: width=2.5, height=3

    plot(1, type="n", axes=FALSE, xlab="", ylab="") # creates an empty plot
    legend("center", legend=legend_pretty_tissues, fill=legend_col, cex=0.75 )  # was: x=1, y=1
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
			
			# set the recurrent/functional mutations
			wt_mut_grps_strings[which(mutations[,results$marker[i]] == 1)] <- "rec. mut."
			
			wt_grp_rows <- which(wt_mut_grps_strings == "wt")
			nonfunc_mut_grp_rows <- which(wt_mut_grps_strings == "non-rec. mut.")
			func_mut_grp_rows <- which(wt_mut_grps_strings == "rec. mut.")
					
			png(filename=paste(
				prefix_for_filename,
				marker_gene,
				"_",
				target_gene,
				"_",
				suffix_for_filename,
				"_",
				"_PMID", pubmed_id_for_filename, ".png",
				sep=""
				),
				# width=5.3, height=4.5, units="in", res=96)
				# width=4.0, height=4.5, units="in", res=96)
				width=4.0, height=4.0, units="in", res=96)
				# width=400, height=400) # default is pixils: , units="in"
				#  res = .... defaults to 72. The smaller this number, the larger the plot area in inches, and the smaller the text relative to the graph itself.
			par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 0.1) ) # SJB: was: width=2.5, height=3, units="in", res=96
			#par(bty="n", tcl=-0.2, mai=c(0.75, 0.7, 0.1, 1.4)) # <-- for legend at right.  SJB: original was: width=2.5, height=3
		
			# boxplot based on all data (wt and mut groups)
			# This print(...) just writes to the console - want to write to file - so maybe add to table then write.table(..
            #print(i)
            #print(zscores[wt_grp_rows,results$target[i]])
            #print(zscores[func_mut_grp_rows,results$target[i]])
			
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
			mtext(paste(marker_gene, "status"), 1, line=2, cex=1.5)
			mtext(paste(target_gene, response_type), 2, line=2.2, cex=1.5)

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
				
				
				if(length(wt_rows_by_tissue) > 0){
					# plot at 1
					# jitter(): https://stat.ethz.ch/R-manual/R-devel/library/base/html/jitter.html
					x <- jitter(rep(1,times=length(wt_rows_by_tissue)), amount=0.33)
					y <- zscores[wt_rows_by_tissue,results$target[i]]
					###print(c(x,y,tissue_cols[j])) # Added by SJB
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
					####print(c(x,y,tissue_cols[j])) # Added by SJB
					points(
						x,
						y,
						col=tissue_cols[j],
						pch=19,
						cex=1.5
						)
				}
			}	
			dev.off()
		}
	}
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







