// Javascript functions for CGDD web interface.

// Good for testing javascript: http://fiddlesalad.com/javascript/

// Tips on making javascript faster:
// Tips on making javascript faster:
//   https://www.smashingmagazine.com/2012/11/writing-fast-memory-efficient-javascript/
//   https://www.smashingmagazine.com/2012/06/javascript-profiling-chrome-developer-tools/

// Can get table cell contents using: http://stackoverflow.com/questions/3072233/getting-value-from-table-cell-in-javascript-not-jquery
// traversing table with js (but using fragment is faster): https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Traversing_an_HTML_table_with_JavaScript_and_DOM_Interfaces
// Using closest() to get immediate parent: http://stackoverflow.com/questions/9085406/passing-this-as-parameter-in-javascript
// Javascript 'this' parameter:  http://stackoverflow.com/questions/14480401/javascript-this-as-parameter
 
// js 'this': http://www.2ality.com/2014/05/this.html


// a simple sprintf() function.
 // For a more comprehensive one, use: https://raw.githubusercontent.com/azatoth/jquery-sprintf/master/jquery.sprintf.js
 // or: http://www.masterdata.se/r/string_format_for_javascript/
 // var msg = 'the department';
 // in doc ready:
 // g: $('#txt').html(sprintf('<span>Teamwork in </span> <strong>%s</strong>', msg));
var sprintf = function(str) {
  var args = arguments,
    flag = true,
    i = 1;

  str = str.replace(/%s/g, function() {
    var arg = args[i++];

    if (typeof arg === 'undefined') {
      flag = false;
      return '';
    }
    return arg;
  });
  return flag ? str : '';
};
/* or simpler is:
function sprintf( format )
{
  for( var i=1; i < arguments.length; i++ ) {
    format = format.replace( /%s/, arguments[i] );
  }
  return format;
}
*/


// The study_info() function is part of the main "index.html" template as it needs each study from the database Study table.
function study_url(study_pmid) {
    if (study_pmid.substring(0,7) === 'Pending') {href = global_url_for_mystudy.replace('mystudy', study_pmid);} // was: '/gendep/study/'+study_pmid+'/';
    else {href = 'http://www.ncbi.nlm.nih.gov/pubmed/' + study_pmid;}
    return href
}


function study_weblink(study_pmid, study) {
//	if (typeof study === 'undefined') {
		return sprintf('<a href="%s" target="_blank">%s</a>', study_url(study_pmid),study[0]);
		// not displaying this now: study = study_info(study_pmid); 	// returns: short_name, experiment_type, summary, "title, authors, journal, s.pub_date"
//        }
//    return sprintf('<a class="tipright" href="%s" target="_blank">%s<span>%s</span></a>', study_url(study_pmid), study[0], study[3] );
}	

function gene_external_links(id, div, all) {
  // id is a dictionary returned by ajax from: view.py : gene_ids_as_dictionary()
  // if 'all' is false, then shows just those links to be displayed below the boxplot images.
  // gene is a row in the Gene table
  // was previously in 'models.py'
  // Note the above sprinf() returns empty string if variable is undefined.
  //console.log("external_links ids=",id)
  links  = '<a class="tip" href="http://www.genecards.org/cgi-bin/carddisp.pl?gene='+id['gene_name']+'" target="_blank">GeneCards<span>Genecards</span></a> ';
  links += div+' <a class="tip" href="http://www.ncbi.nlm.nih.gov/gene/'+id['entrez_id']+'" target="_blank">Entrez<span>Entrez Gene at NCBI</span></a> '; 
  links += div + sprintf(' <a class="tip" href="http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=%s" target="_blank">Ensembl<span>Ensembl Gene</span></a> ', id['ensembl_id']);
  links += div + sprintf(' <a class="tip" href="http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id=%s" target="_blank">HGNC<span>HUGO Gene Nomenclature Committee</span></a> ', id['hgnc_id']);  
  if (all) {
    links += div + sprintf(' <a class="tip" href="http://vega.sanger.ac.uk/Homo_sapiens/Gene/Summary?g=%s" target="_blank">Vega<span>Vertebrate Genome Annotation</span></a> ', id['vega_id']);
    links += div + sprintf(' <a class="tip" href="http://www.omim.org/entry/%s" target="_blank">OMIM<span>Online Mendelian Inheritance in Man</span></a> ', id['omim_id']);
    links += div + sprintf(' <a class="tip" href="http://www.cancerrxgene.org/translation/Search?query=%s" target="_blank">CancerRxGene<span>CancerRxGene search</span></a> ', id['gene_name']);
	}
  links += div + sprintf(' <a class="tip" href="http://www.cbioportal.org/ln?q=%s" target="_blank">cBioPortal<span>cBioPortal for Cancer Genomics</span></a> ', id['gene_name']);
  if (id['cosmic_id'] != '') {links += div + sprintf(' <a class="tip" href="http://cancer.sanger.ac.uk/cosmic/gene/analysis?ln=%s" target="_blank">COSMIC<span>Catalogue of Somatic Mutations in Cancer</span></a> ', id['cosmic_id']);}
  links += div + sprintf(' <a class="tip" href="https://cansar.icr.ac.uk/cansar/molecular-targets/%s/" target="_blank">CanSAR<span>CanSAR</span></a>', id['uniprot_id']);
  return links;
}

function show_search_info(data) {
  var qi = data['query_info']; // best to test if this exists in the query
  //console.log(qi);
  var search_by = qi['search_by'];
  $("#gene_search_by").html(search_by=='target' ? 'Target' : 'Driver');
  var gene = qi['gene_name'];
  alert("gene: '"+gene+"'")
  if (gene != global_selected_gene) {alert("ERROR: query returned search by gene("+gene+") != global_selected_gene("+global_selected_gene+")")}
  $("#gene_name").html(gene);
  alert("gene: '"+gene+"'")
  alert("gene html: '"+$("#gene_name").html()+"'")
  $("#gene_synonyms").html(qi['gene_synonyms']);
  $("#gene_full_name").html(qi['gene_full_name']);
  // was: $("#gene_weblinks").html(qi['gene_weblinks']);
  $("#gene_weblinks").html(gene_external_links(data['gene_ids'], '|', true));
  
  $("#result_info").html( "For "+ search_by +"gene <b>" + gene + "</b>, a total of <b>" + qi['dependency_count'] + " dependencies</b> were found in " + qi['histotype_details'] + " in "+qi['study_details'] );

  var download_csv_url = global_url_for_download_csv.replace('mysearchby',search_by).replace('mygene',gene).replace('myhistotype',qi['histotype_name']).replace('mystudy',qi['study_pmid']);
  
  $("download_csv_button").html("Download as CSV file"); // reset as could have been set to "Downloading CSV file".
  // console.log("download_url: ",download_csv_url);
  //var button_event = "window.open('" + download_url + "');"
  //console.log(button_event)
  // $("#download_csv")  .click( button_event );
  
    // ******
   // Better to use the form:
   // $("#download_csv_form").action(function() { ......	? return false;
   // http://stackoverflow.com/questions/11620698/how-to-trigger-a-file-download-when-clicking-an-html-button-or-javascript
   
   // eg: or put a button inside a link: <a href="file.doc"><button>Download!</button></a>
   //Link. Then it'll work fine  without JavaScript available. It also offers more of the traditional affordances users might expect from a download link, such as right-click-save-as, or drag-and-drop.

   // But maybe is a Chrome problem:
   // "The headers are correct, express sets them properly automatically, it works in other browsers as indicated, putting html 5 'download' attribute does not resolve, what did resolve it is going into the chrome advanced settings and checking the box "Ask where to save each file before downloading".
   // After that there was no "Resource interpreted as document...." error reported as in the title of this issue so it appears that our server code is correct, it's Chrome that is incorrectly reporting that error in the console when it's set to save files to a location automatically."


   // $("#download_csv_form").attr("action", download_csv_url);
   $("#download_csv_form")
     .attr("action", download_csv_url)
     .submit(function( event ) {
      $("#download_csv_button").html('Downloading CSV file')
	//return true;
   });



/*  
  $("#download_csv_button").click(function() {
	  $("#download_csv").html('Downloading CSV file.');
	  // window.location = download_csv_url; // provided the server sets Content-Disposition: attachment!
	  // or: window.open(download_csv_url); // which briefly open a new browser tab for the download.
	  //$("#download_csv").html('File downloaded'); // but updates text before file is downloaded.
	  // Using the above "window.location = ..." causes Chrome to give warning in console about: 
	  //   "cgdd_functions.js:109 Resource interpreted as Document but transferred with MIME type text/csv: ...."
	  // So use a link instead, or can use a hidden link on the page, eg: <a href="fileLink" download="filename">Download</a>, or a form ....
	  var downloadLink = document.createElement('a');
	  downloadLink.href = download_csv_url;
	  downloadLink.download = download_csv_url; // but this 'download' attribute is html5 so limited browser support possibly
	  document.body.appendChild(downloadLink);  // as link has to be on the document.
	  downloadLink.click();	  
	  }); 
*/	  
}





function setup_qtips() {
// ideas: filter: http://stackoverflow.com/questions/22262325/how-to-create-a-tooltip-for-the-filter-widget-of-the-jquery-tablesorter-plugin

// qtip Examples: http://stackoverflow.com/questions/2950004/how-to-use-jquery-qtip-simple-example-please
// examples inside a html table: http://jsfiddle.net/qTip2/T9GHJ/
// https://forum.jquery.com/topic/apply-tooltip-to-each-cells-for-a-particular-table
//  http://jsfiddle.net/qTip2/qcwV4/
//  http://qtip2.com/demos#positioning-zindex

//dataTable({
//    bLengthChange: false,
//    bFilter: false
//  })
  console.log("Adding qtips to table")
// selector was:  'tr[data-browser]'
	// set up the qtips
  $('#result_table_tbody td')
  .on('mouseenter', null, function (event) {
    //var browser = $(this).data('browser');
    var browser = 'Hello';
	
    $(this).qtip({
        overwrite: false,
        content: 'Test', // '<img src="http://media1.juggledesign.com/qtip2/images/browsers/64-' + browser + '.png" alt="' + browser + '"/>',
        position: {
            my: 'right center',
            at: 'left center',
            target: $('td:eq(1)', this),
            // viewport: $('#datatables')
        },
        show: {
            event: event.type,
            ready: true
        },
        hide: {
            fixed: true
        }
    }, event); // Note we passed the event as the second argument. Always do this when binding within an event handler!
   // =================================== end of qtips setup ===================
   
   // http://stackoverflow.com/questions/16059315/tooltip-on-hover-of-elements-generated-by-ajax-request
   // $(document).on('hover', '.best-item-option', function(){        
   // $('.best-item-option').tooltipster();
   // $('.best-item-option').tooltipster('show');
   //});
   
});
}

	
function populate_table(data,t0) {
  var html = '';
	// The position of the P-value column needs to correspond with the index.htm javascript for "filter-select:"
	
	// PLOT THE BOXPLOT AND LEGEND SEPARATELY - LEGEND MIGHT BE SPECIFIC TO THE STUDY - ie. Achilles has more tissues, and doesn't have some tissues - so "Legend_PMID.....png" #}

	/*
	// By lines
    var lines = this.result.split('\n');
    for(var line = 0; line < lines.length; line++){
        // By tabs
        var tabs = lines[line].split('\\t');
        for(var tab = 0; tab < tabs.length; tab++){    
                alert(tabs[tab]);
        }   
    }
  };
  */
	//str.split(',') // or use '\t' as using comma assumes that no fields contain a comma - checked before data was added to the database.
	// if need to parse CSV that has quoted strings containing commas, then use: https://github.com/evanplaice/jquery-csv/
	var qi = data['query_info'];
	var search_by = qi['search_by'];
	
    var driver,target, search_by_driver;
	switch(search_by) {
		case 'driver':
	       $("#dependency_col_name").html('Dependency');
		   search_by_driver = true;
		   driver = qi['gene_name'];
		   break;
		case 'target':
	       $("#dependency_col_name").html('Driver');
		   search_by_driver = false;
		   target = qi['gene_name'];
		   break;
		default: alert("Invalid search_by: "+search_by);
	}

	results = data['results']
	//console.log(results);
	
	for (var i=0; i<results.length; i++) {   // for dependency in dependency_list	  
	  d = results[i]; // d is just a reference to the array, not a copy of it, so should be more efficient and tidier than repeatidly using results[i]
	  // result array indexes:
	  // igene can be either driver or target depending on 'search_by'.
	  var igene=0, iwilcox_p=1, ieffect_size=2, ihistotype=3, istudy_pmid=4, iinteraction=5, iinhibitors=6, itarget_variant=7; //(will remove target_variant later - just used for now to ensure get the correct Achilles variant boxplot image)
	  // In javascript array indexes are represented internally as strings, so maybe using string indexes is a bit faster??
	  var study = study_info(d[istudy_pmid]); // name,type,summary,details for 'study_pmid'
	  // perhaps 'map ......join' might be more efficient?
	  var comma = "', '";  // ie. is:  ', '
	  // An alternative to building the html as a string, is to directly modify the table using javascript.
	  // Pass the unformatted effect size, as the html tags could mess up as embedded inside tags.
	  // alternatively could pass 'this', then use next() to find subsequent columns in the row, or keep the data array globally then just specify the row number as the parameter here, eg: plot(1) for row one in the array.
      if (search_by_driver) {target = d[igene];}
      else {driver = d[igene];}
		
	  var plot_function = "plot('" + driver + comma + target +comma+ d[ihistotype] +comma+ d[istudy_pmid] +comma+ d[iwilcox_p] +comma+ d[ieffect_size] +comma+ d[itarget_variant] +"');";

      // Another way to pouplatte table is using DocumentFragment in Javascript:
      //      https://www.w3.org/TR/DOM-Level-2-Core/core.html#ID-B63ED1A3
	  
	  // *** GOOD: http://desalasworks.com/article/javascript-performance-techniques/

	  var darkgreen_UCD_logo  = '#00A548';
	  var midgreen_SBI_logo   = '#92C747';
	  var lightgreen_SBI_logo = '#ADD17C';
	  
	  var val = parseFloat(d[ieffect_size]); // convert to float value
      if      (val >= 90) {bgcolor=' style="background-color:'+darkgreen_UCD_logo+'"'}
	  else if (val >= 80) {bgcolor=' style="background-color:'+midgreen_SBI_logo+'"'}
	  else if (val >= 70) {bgcolor=' style="background-color:'+lightgreen_SBI_logo+'"'}
	  else {bgcolor = '';}
	  var effectsize_cell = '<td'+bgcolor+'>' + d[ieffect_size] + '</td>';

	  val = parseFloat(d[iwilcox_p]); // This will be in scientific format, eg: 5E-4
      if      (val <= 0.0001) {bgcolor=' style="background-color:'+darkgreen_UCD_logo+'"'}
	  else if (val <= 0.001)  {bgcolor=' style="background-color:'+midgreen_SBI_logo+'"'}
	  else if (val <= 0.01)   {bgcolor=' style="background-color:'+lightgreen_SBI_logo+'"'}
	  else {bgcolor = '';}	  
	  var wilcox_p_cell = '<td'+bgcolor+'>' + d[iwilcox_p].replace('E', ' x 10<sup>') + '</sup></td>';
/*
	  switch (d[iinteraction]) { // This will be in scientific format, eg: 5E-4
        case 'Highest': bgcolor=' style="background-color:'+darkgreen_UCD_logo+'"';  break;
	    case 'High':    bgcolor=' style="background-color:'+midgreen_SBI_logo+'"'    break;
	    case 'Medium':  bgcolor=' style="background-color:'+lightgreen_SBI_logo+'"'; break;
	    default: bgcolor = '';
	  }
	  var interaction_cell = '<td'+bgcolor+'>'+d[iinteraction]+'</td>';
*/
	  var interaction_cell = (d[iinteraction] === 'Y') ? '<td style="background-color:'+darkgreen_UCD_logo+'">Yes</td>' : '<td></td>';

	  html += '<tr>'+
        '<td gene="'+d[igene]+'"><a href="javascript:void(0);" onclick="'+plot_function+'">' + d[igene] + '</a></td>' + // was class="tipright" 
		// In future could use the td class - but need to add on hoover colours, etc....
		// '<td class="tipright" onclick="plot(\'' + d[0] + '\', \'' + d[4] + '\', \'' + d[3] +'\');">' + d[0] + '</td>' +
         wilcox_p_cell + 
		 effectsize_cell +
        '<td>' + histotype_display(d[ihistotype]) + '</td>' +
		'<td study="'+d[istudy_pmid]+'">' + study_weblink(d[istudy_pmid],study) + '</td>' + // but extra text in the table, and extra on hover events so might slow things down.
		// '<td>' + study_weblink(d[istudy_pmid], study) + '</td>' + // but this is extra text in the table, and extra on hover events so might slow things down.
		// '<td>' + study[0] + '</td>' + // study_weblink
		//'<td>' + study[1] + '</td>' +  // <a href="#" class="tipleft"> ...+'<span>' + study_summary + '</span>
		//'<td><a href="#" class="tipleft">' + study[1] + '<span>' + study[2] + '</span></td>' +
		'<td exptype="'+d[istudy_pmid]+'">' + study[1] + '</td>' + // experiment type. The 'exptype=""' is use by tooltips
        interaction_cell +
		// '<td>' + d[iinteraction] + '</td>' +  // 'interaction'
		
	    '<td>' + d[iinhibitors] + '</td>' +  // 'inhibitors'
		'</tr>';  // The newline cahracter was removed from end of each row, as the direct trigger update method complains about undefined value.
/*
	  html += '<tr>'+
		'<td>A</td>' +
		'<td>B</td>' + // inlined this replace()
        '<td>C</td>' + 
		'<td>D</td>' + // study_weblink
		'<td>E</td>' +
		'<td>F</td>' +
		'<td>G</td>' +  // <a href="#" class="tipleft"> ...+'<span>' + study_summary + '</span>
		'<td>H</td>' +  // 'interaction'
		'</tr>';
*/		
	  // To minimise the size of the transfer from webserver, used single characters for these dependency fields:
	  //  t=target, p=wilcox_p, e=effect_size, s=study, h=histotype, i=inhibitors, a=interaction
	  /*
      html += '<tr>'+
        '<td><a class="tipright" href="plot(\"' + d['t'] + '\");">' + d['t'] + '</a></td>' +
		'<td>' + d['p'].replace('E', ' x 10<sup>')+'</sup></td>' + // inlined this replace()
        '<td>' + d['e'] + '</td>' + 
		'<td>' + study[0] + '</td>' + // study_weblink
        '<td>' + histotype_display(d['h']) + '</td>' +
		'<td>' + d['i'] + '</td>' +
		'<td>' + study[1] + '</td>' +  // <a href="#" class="tipleft"> ...+'<span>' + study_summary + '</span>
		'<td>' + d['a'] + '</td>' +  // 'interaction'
		'</tr>\n';
		*/
	}


	
    //	var t1 = performance.now();
    // console.log("String Loop took " + (t1 - t0) + " milliseconds.")
	
	// console.log(html);
    //$("#result_table_tbody").replaceWith(html);
	console.log("Data formatted as html: ",performance.now()-t0); t0 = performance.now();
	
	// $("#result_table_tbody").html(html);
	$("#result_table_tbody").html(html);
	console.log("Data added to table tbody: ",performance.now()-t0); t0 = performance.now();
	//setup_qtips();
	
	// or from: https://github.com/Mottie/tablesorter/blob/master/docs/example-add-rows.html
	//resort = false;
	//$rows = $(html)
	//$("#result_table_tbody").append($rows)
    //$("#result_table").trigger('addRows', [$rows, resort]);
	
	// $tbodies = $( 'table' ).
	// $("table").trigger("updateCache", [ callback, $tbodies ] );
	
    triggercallback = function( table ){
     //   alert( 'update applied' );
	 console.log("Table updated: ",performance.now()-t0); t0 = performance.now();
    };
    $("#result_table").trigger("updateRows", [ false, triggercallback ]); // let the plugin know that we made a update, updates the updates the cache from the tbody.  Can use "updateRows" instead. ("updateRows was added to work around the issue of using jQuery with the Prototype library. Triggering an "update" would make Prototype clear the tbody")
	// or: .trigger( 'addRows', [ $row, resort, callback ] );
	
	// triggered event method:
    //$table.trigger( 'addRows', [ html, true ] );

    // direct method:
	//var $table = $( "#result_table" );
    //var config = $table[ 0 ].config;
	//alert(html);
    //$.tablesorter.addRows( config, html, true );  // So instead of making a jQuery object, appending it to the table, then passing the reference to the method, you can just pass a string. This method doesn't work if a table has multiple tbodies, because the plugin doesn't know where you want to add the rows.
	
	
	
//	Maybe need to reset the scroller height to make the added rows visible?
//	Also see the addRows() functions: https://mottie.github.io/tablesorter/docs/#methods
	
//	Use config.totalRows to see the number of rows.	
//	var $table = $( 'table' ),
//    config = $table[ 0 ].config;

	return t0;
}



function sup10_format(num) {
  // Could also replace pythons leading zero in the exponent, but already replaced on server in the views.py script, eg: if (num.indexOf("E-0")>=0) {return num.replace("E-0", " x 10<sup>-")+"</sup>";}
  return num.replace("E", " x 10<sup>")+"</sup>"; 
}

function format_gene_info_for_tooltip(data) {
  var synonyms = data['synonyms'];
  if (synonyms != '') {synonyms = ' | '+synonyms}
  return '<b>'+data['gene_name'] + '</b>' + synonyms +'<br/><i>' + data['full_name']+'</i>';
  }

function is_form_complete() {
  // As the autocomplete form permits text that doesn't match any driver:
  var search_by = document.getElementById("search_by").value;
  var g = document.getElementById("gene").value;
  if (g == null || g == "") {
    alert("Search '"+search_by+" gene name' field needs a value entered");
    return false;
    }
  
  var found = false;
  if (search_by = 'driver') {
    for (var i=0; i<driver_array.length; i++) {
      if (g == driver_array[i]['value']) {
        found = true;
        break;
      }
    }
  }
  else if (search_by = 'target') {
      for (var i=0; i<target_array.length; i++) {
      if (g == target_array[i]['value']) {
        found = true;
        break;
      }
    }
  }
  else {alert('Invalid search_by '+search_by)}
  
  if (found == false) {alert("The "+search_by+" gene value: '"+g+"' doesn't match any "+search_by+" in the list. Please select a "+search_by+" gene.");}
  return found;
  }



// Could possibly use $(this).parent() to set background colour for row, then store this in global variable, then in fancybox close event set row color back to normal...eg: http://stackoverflow.com/questions/4253558/how-to-get-the-html-table-particullar-cell-value-using-javascript
function show_fancybox(driver, target, histotype, study_pmid, wilcox_p, effect_size, target_info, target_variant) {
  // This is a separate function from plot(...) as this can be a called when Ajax succeeds.

// eg: http://jsfiddle.net/STgGM/
// Another way to draw the boxplots on HTML canvas using, eg: https://github.com/flot/flot/blob/master/README.md
// http://www.flotcharts.org/
// and use a library for IE<9

  // var driver = global_selected_gene;
  
  var boxplot_image = driver+'_'+target+target_variant+'_'+histotype+'__PMID'+study_pmid+'.png';

  var url_boxplot = global_url_static_boxplot_dir + driver.substring(0,1) + '/' + boxplot_image; // Images are stored in subdirectiories A, B, C,...X,Y,Z (using the first letter of the image name) which might speed up access to the files on the server.
  var boxplot_width = 384;
  var boxplot_height = 384;
  
  var legend_size = 'w16_cex8';  var legend_width = 153; //for w16_cex8
  var legend_height = 384;
  // other sizes: 'w20_cex9'; 'w18_cex85'; 'w16_cex8'; 'w15_cex75';
  var legend_image = 'Legend_PMID'+study_pmid+'_'+legend_size+'.png';
  var url_legend = global_url_static_image_dir +legend_image;
  // Putting a table around the box plots as otherwise if click on gene near bottom of page the fancybox makes tall box as probably tries to put legend below the boxplot
  // For table add: style="padding:0;border-collapse: collapse;" table {border-spacing: 2px;} td    {padding: 0px;} cellspacing="0" (see: http://stackoverflow.com/questions/339923/set-cellpadding-and-cellspacing-in-css )
  var mycontent = '<table align="center" style="padding:0; border-collapse: collapse; border-spacing: 0;"><tr><td style="padding:0;"><img src="' + url_boxplot + '" width="'+boxplot_width+'" height"'+boxplot_height+'" alt="Loading boxplot image...."/></td>' + '<td style="padding:0;"><img src="' + url_legend + '" width="'+legend_width+'" height"'+legend_height+'"/></td></tr></table>';
 // console.log(mycontent);
  var study = study_info(study_pmid);
//console.log(mycontent);
//console.log(gene_info_cache[target]);
//console.log(target_ids);
    
  var plot_title = '<p align="center" style="margin-top: 0;"><b>'+driver+'</b> altered cell lines have an increased dependency upon <b>'+target+'</b><br/>(p='+wilcox_p.replace('E', ' x 10<sup>')+'</sup> | effect size='+effect_size+'% | Tissues='+ histotype_display(histotype) +' | Source='+ study[0] +')';

  if (typeof target_info === 'undefined') {plot_title += '<br/>Unable to retrieve synonyms and external links for this gene';}
  else {
      if (target !== target_info['gene_name']) {alert("Target name:"+target+" != target_info['gene_name']:"+target_info['gene_name'] );}
	  var target_external_links = gene_external_links(target_info['ids'], '|', false); // returns html for links to entrez, etc. The 'false' means returns the most useful selected links, not all links.
	  var target_full_name  = '<i>'+target_info['full_name']+'</i>';
	  var target_synonyms   = target_info['synonyms'];
	  if (target_synonyms !== '') {target_synonyms = ' | '+target_synonyms;}
	  plot_title += '<br/><b>'+target+'</b>'+target_synonyms+', '+target_full_name+'<br/>'+target+' Links: '+target_external_links;
	  }
  plot_title += '</p>';
  
//console.log(plot_title);

  $.fancybox.open({
  //$(".fancybox").open({
    // href: url_boxplot,
    preload: 0, // Number of gallary images to preload
    //minWidth: 550, // To enable boxplot and image to be side-by-side, rather than legend below boxplot
    //maxHeight: 550,
	autoSize: false, // otherwise it resizes too tall.
    padding: 2,  	// is space between image and fancybox, default 15
    margin:  2, 	// is space between fancybox and viewport, default 20
	width:  boxplot_width+legend_width+8, // default is 800
	height: boxplot_height + 8, // default is 600 /// the title is below this again, ie. outside this, so the 25 is just to allow for the margins top and bottom 
    aspectRatio: true,
    fitToView: false,
    arrows: false,
	closeEffect : 'none',
    helpers: {
        title: {
            type: 'inside'
        },
        overlay: {
            showEarly: false  // as otherwise incorrectly sized box displays before images have arrived.
        }
    },

    // href="{#% static 'gendep/boxplots/' %#}{{ dependency.boxplot_filename }}" 
    // or $(...).content - Overrides content to be displayed - maybe for inline content
	type: 'html', // 'iframe', // 'html', //'inline',
    //content: 
	content: mycontent,
    title: plot_title,
   });
   
   return false; // Return false to the caller so won't move on the page
}
  


//function plot(index) { // The index number of the dependency in the array
function plot(driver, target, histotype, study_pmid, wilcox_p, effect_size, target_variant) { // The index number of the dependency in the array
//console.log(target);
  var target_info;
  if (target in gene_info_cache) {
	target_info = gene_info_cache[target];
	show_fancybox(driver, target, histotype, study_pmid, wilcox_p, effect_size, target_info, target_variant);
	}
  else {
	// The target_info will usually have already been retreived by hoovering over the target in table, but if user clicked fast, then might not have been retreived yet.
	// Might be better to get the ids after the fancybox has displayed - ie. on fancybox's loaded .... method.
    $.ajax({
      url: global_url_gene_info_for_mygene.replace('mygene',target),
      dataType: 'json',
      })
      .done(function(target_info, textStatus, jqXHR) {  // or use .always(function ...
         if (target_info['success']) {
			gene_info_cache[target] = target_info; // cache data so can retrieve faster in future.
		 }
		 else {console.log("Error: "+target_info['message'])}
		 })
	  .fail(function(jqXHR, textStatus, errorThrown) {
		 console.log("Ajax Failed: '"+textStatus+"'  '"+errorThrown+"'");
		 // target_info = undefined;
         })
	  .always(function() {
	  	 show_fancybox(driver, target, histotype, study_pmid, wilcox_p, effect_size, target_info, target_variant);
	     });
    }
	
    return false; // Return false to the caller so won't move on the page as is called from a href="...
}


/*
			<a class="fancybox tipright" rel="group" href="{% static 'gendep/boxplots/' %}{{ dependency.boxplot_filename }}" data-fancybox-title='<b>{{ dependency.driver.gene_name }}</b> altered cell lines have an increased dependency upon <b>{{ dependency.target.gene_name}}</b><br/>(p={{ dependency.wilcox_p_power10_format|safe }} | Tissues={{ dependency.get_histotype_display }} | Source={{ dependency.study.weblink|safe }})<br/>{{ dependency.target.gene_name }} links: {{ dependency.target.external_links_on_boxplot|safe }}</font>' >{{ dependency.target.gene_name }} &nbsp; <font size="-2">{{ dependency.target.prev_names_and_synonyms_spaced }}</font><span>{{ dependency.target.full_name }}: {{ dependency.target.prev_names_and_synonyms_spaced }}</span></a></td>
#}
	
// content 	

    //+power10_format(d..wilcox_p) +' | Tissues='+ get_histotype_display(d.histotype) +' | Source='+ study_weblink(study_pmid) +')<br/>'+target+'links: '+ external_links_on_boxplot(d.....) +'</font>';
		
		  // the data can be stored as an array of in fields with id names.
				/*
	{{ dependency.target.gene_name }} &nbsp; <font size="-2">{{ dependency.target.prev_names_and_synonyms_spaced }}</font>
		<span>{{ dependency.target.full_name }}: {{ dependency.target.prev_names_and_synonyms_spaced }}</span>
		
		</a>
		
		</td>
*/
  
  
  
/*
OLD CODE TO DELETE:

function external_links_on_boxplot(index, div='|') {
    // gene is a row in the Gene table
    // This is a shortened form of the above as not all needed:
    // Building these links here, rather than in template as are used twice in the template:
	// Could either store these links in dependency array, or use an ajax call to server when loading the boxplot image.
	return(
        '<a class="tip" href="http://www.genecards.org/cgi-bin/carddisp.pl?gene='+gene_name+'" target="_blank">GeneCards<span>Genecards</span></a> ' +
        div+' <a class="tip" href="http://www.ncbi.nlm.nih.gov/gene/'+entrez_id+'" target="_blank">Entrez<span>Entrez Gene at NCBI</span></a> ' +
        div+' <a class="tip" href="http://www.ensembl.org/Homo_sapiens/Gene/Summary?g='+ensembl_id+'" target="_blank">Ensembl<span>Ensembl Gene</span></a> ' +
        div+' <a class="tip" href="http://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id='+hgnc_id+'" target="_blank">HGNC<span>HUGO Gene Nomenclature Committee</span></a> ' +
        div+' <a class="tip" href="http://www.cbioportal.org/ln?q='+gene_name+'" target="_blank">cBioPortal<span>cBioPortal for Cancer Genomics</span></a> ' +
        div+' <a class="tip" href="http://cancer.sanger.ac.uk/cosmic/gene/analysis?ln='+gene_name+'" target="_blank">COSMIC<span>Catalogue of Somatic Mutations in Cancer</span></a> ' +
        div+' <a class="tip" href="https://cansar.icr.ac.uk/cansar/molecular-targets/'+uniprot_id+'/" target="_blank">CanSAR<span>CanSAR</span></a>' )
}


function show_plot(driver,target)
  {
  document.getElementById('plot_title').innerHTML = '<b>' + target + ' vs ' + driver + '</b>'; 
  if (driver=='ERBB2' && target=='MAP2K3')
    {
    // Should use { % static .... % } below in future:
    // document.getElementById("plot_image").src = '../static/gendep/' + target + '_vs_' + driver + '.png'; // eg: MAP2K3_vs_ERBB2.png
    document.getElementById("plot_image").src = '{% static 'gendep/boxplots/' %}' + driver + '_' + target + '.png'; // eg: MAP2K3_vs_ERBB2.png
    document.getElementById('plot_description').innerHTML = 'ERBB2 mutant cell lines have an increased dependency upon MAP2K3 (p=10-4 | Tissues=muliple | Source=Campbell et al (2015))'; 
    }
  else
    {
    document.getElementById("plot_image").src = '';
    document.getElementById('plot_description').innerHTML = 'No plot available';
    }
  }


boxplot_filename

  $fancybox.open([{
	  
	  
  $(...).href: "{% static 'gendep/boxplots/' %}"+driver+'_'target+'__PMID'+pmid+'.png'; // href="{#% static 'gendep/boxplots/' %#}{{ dependency.boxplot_filename }}" 
  // or $(...).content - Overrides content to be displayed - maybe for inline content
  
  $(...).title: '<b>'+driver+'</b> altered cell lines have an increased dependency upon <b>'+target+'</b><br/>(p='+wilcox_p_power10_format|safe +' | Tissues='+ dependency.get_histotype_display +' | Source='+ dependency.study.weblink|safe +')<br/>'+target+'links: '+ dependency.target.external_links_on_boxplot|safe +'</font>';
		
		  // the data can be stored as an array of in fields with id names.
				
	{{ dependency.target.gene_name }} &nbsp; <font size="-2">{{ dependency.target.prev_names_and_synonyms_spaced }}</font>
		<span>{{ dependency.target.full_name }}: {{ dependency.target.prev_names_and_synonyms_spaced }}</span>
		
		</a>
		
		</td>


  // data-fancybox-title=

	Overrides content source link String; Default value: null



    		<a class="fancybox tipright" rel="group" href="{% static 'gendep/boxplots/' %}{{ dependency.boxplot_filename }}" data-fancybox-title='<b>{{ dependency.driver.gene_name }}</b> altered cell lines have an increased dependency upon <b>{{ dependency.target.gene_name}}</b><br/>(p={{ dependency.wilcox_p_power10_format|safe }} | Tissues={{ dependency.get_histotype_display }} | Source={{ dependency.study.weblink|safe }})<br/>{{ dependency.target.gene_name }} links: {{ dependency.target.external_links_on_boxplot|safe }}</font>' >{{ dependency.target.gene_name }} &nbsp; <font size="-2">{{ dependency.target.prev_names_and_synonyms_spaced }}</font><span>{{ dependency.target.full_name }}: {{ dependency.target.prev_names_and_synonyms_spaced }}</span></a></td>
#} 		


		
				<a class="fancybox tipright"
		rel="group" 
*/