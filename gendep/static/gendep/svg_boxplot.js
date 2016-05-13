
// SVGMagic would enable older browsers to view the SVG imagers: https://github.com/dirkgroenen/SVGMagic  
  
// SVG javascript libraries:
// 1) svg.js:  http://svgjs.com/ for manipulating and annimations (15 kb gzipped)
// 2) snap svg:  http://snapsvg.io/
// 3) Raphael - 20kb when gzipped:
//      http://dmitrybaranovskiy.github.io/raphael/
//      https://github.com/DmitryBaranovskiy/raphael supports older browsers via VML (eg. IE<=8 and early Safari)
//      https://dev.opera.com/articles/raphael-javascript-api-for-svg/
// 4) Pablo - http://pablojs.com/ a small library for SVG
// 5) D3.js:  http://d3js.org/
// 6) Velocity.js: http://julian.com/research/velocity/ (for fast annimation, doesn't use jQuery)

// 7) Eve "event helping library" https://github.com/adobe-webplatform/eve
// 8) Plot.ly (commercial graph library, uses D3) https://plot.ly/javascript/box-plots/

// Older plotting library for IE7, IE8: http://www.jqplot.com/index.php


// Box plot libraries: https://plot.ly/javascript/box-plots/
//   http://forum.highcharts.com/highcharts-usage/bee-swarm-t34154/

// A Nice graph: http://i.stack.imgur.com/qDuUN.png

// D3 many good graphs: https://github.com/mbostock/d3/wiki/Gallery

// D3: http/ 3: Dchristophermanning.org/projects/building-cubic-hamiltonian-graphs-from-lcf-notation

// D3: Scatter plot matrix: http://bl.ocks.org/mbostock/3213173

// D3:Fisheye:  https://bost.ocks.org/mike/fisheye/

// Hive network plot:   https://bost.ocks.org/mike/hive/


// gene expression: http://sulab.org/2013/02/data-chart-plugin-beta/

// d3: Dependency wheel: http://www.redotheweb.com/DependencyWheel/

// Gene portal wiki:
// https://en.wikipedia.org/wiki/HER2/neu


// BioGPS:  http://biogps.org/#goto=genereport&id=2064
// and its plugins.


// Lots of different ToolTip libraries:  http://www.bypeople.com/jquery-tooltip/
// eg: SimpleTips: http://craigsworks.com/projects/simpletip/#
// TinyTips: https://github.com/Sweefty/tinytip


// Lightboxes: http://js-tutorial.com/category/lightbox-7
//    eg: Simple LightBox: http://js-tutorial.com/simple-lightbox-1502

// An SVG tutorial: http://svgtutorial.com/manipulating-svg-with-javascript/


/*
// example of beeswarm jitter for high charts:
$(function () {

      var jspace = 50;
      
    var data = [83.2,85.2,93.2,79.2,82.2,91.2,81.0,81.0,85.5,85.2,84.8,87.2,91.1,78.0,81.5,82.2,84.3,95];
    data = data.sort();
    var xydata = [];
    var l = undefined;
    var c = 1;
    for (var i = 0; i < data.length; i++) {
       d = data[i];
       if (Math.floor(d) !== l){
         l = Math.floor(d);
        c = 1;
      } else {
         c += 1;
      }
      m = (c % 2 == 0) ? 1 : -1;
      j = (Math.floor(c/2) * m)/jspace;
      // Don't let jitter get too big
      while(j > 1 || j < -1){
         var n = Math.floor(Math.abs(j)) + 1;
         j = (Math.floor(c/2) * m)/(jspace*n);
      }
      xydata.push([j,d]);
    }
   
    $('#container').highcharts({

            title: {text: 'Example Beeswarm Plot' },
        xAxis: {
            categories: ['% Aligned']
        },
        yAxis: {title: {text: null}},
            legend: { enabled: false },
        series: [{
            name: 'Alignment',
            type: 'scatter',
            data: xydata
        }]

    });
});
*/

  
/*
// Dynamically creating the SVG:
var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
// svg.setAttribute('style', 'border: 1px solid black');
svg.setAttribute('width', '600');
svg.setAttribute('height', '250');
svg.setAttributeNS("http://www.w3.org/2000/xmlns/", "xmlns:xlink", "http://www.w3.org/1999/xlink");
document.body.appendChild(svg);
*/  
// For hyperlinks from SVG elements: http://stackoverflow.com/questions/20539196/creating-svg-elements-dynamically-with-javascript-inside-html

  
// edge effects: http://www.software-architects.com/devblog/2015/03/22/Shades-of-Gray-in-SVG---How-to-Get-a-Sharp-Black-Line

// Fills and Strokes:    https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Fills_and_Strokes

  
var tissue_colours = {
   // Using "select distinct(histotype) from gendep_dependency;" found only 9 tissues in current 23 driver dependency data (plus PANCAN)
      
   // Using "select boxplot_data from gendep_dependency where (boxplot_data like "%LIVER%" ) limit 1;"
   // 0 rows returned in 32527ms from: select boxplot_data from gendep_dependency where (boxplot_data like "%LIVER%" );
   // BUT all the other tissues below do appear in the boxplot_data:
	
   //"BONE":         "yellow",
  "OSTEOSARCOMA": "yellow", // same as BONE above
  "BREAST":       "deeppink",  // Colt only contains Breast
  "LUNG":         "darkgrey",
  "HEADNECK":     "firebrick",  // Not in Achilles data  (*** THIS "firebrick4" COLOUR NOT WORKING IN IE SVG) - NOT in dependency data from the 23 drivers, so don't show on legend.
  "PANCREAS":     "purple",
  "CERVICAL":     "blue",  // Not in Achilles data. Not in 23 driver dependicies
  "OVARY":        "cadetblue",
  "OESOPHAGUS":   "green",
  "ENDOMETRIUM":  "orange",     // Not in 23 driver dependency data
  "CENTRAL_NERVOUS_SYSTEM": "darkgoldenrod",  // *** THIS "darkgoldenrod4" COLOUR NOT WORKING IN IE SVG
  "HAEMATOPOIETIC_AND_LYMPHOID_TISSUE": "darkred",  // Not in Campbell
  "INTESTINE":    "saddlebrown",// Not in Campbell
  "KIDNEY":       "indianred",  // Not in Campbell,  Not in 23 driver dependency data
  // "LIVER":        "slategray", // Not in Campbell,  Not in 23 driver dependency data, so don't display on legend
  "PROSTATE":     "turquoise",  // Not in Campbell,  Not in 23 driver dependency data
  "SKIN":         "peachpuff",  // Not in Campbell,  Not in 23 driver dependency data
  "SOFT_TISSUE":  "lightgrey",  // Not in Campbell,  Not in 23 driver dependency data
  "STOMACH":      "black",      // Not in Campbell,  Not in 23 driver dependency data
  "URINARY_TRACT":"yellowgreen" // Not in Campbell,  Not in 23 driver dependency data
  };
    
//var driver = "SEMG2", target = "CAMK1", wilcox_p = "1.8e-2", effect_size = "0.78", histotype="Pan cancer", study="Campbell(2016)";
// was: "range,-8,2;wt_box,-2.57,-1.15,-0.58,-0.09,1.28;mu_box,-3.01,-3.01,-2.15,-0.62,-0.52;
//var boxplot_csv = "80,-8,2,-2.57,-1.15,-0.58,-0.09,1.28,-3.01,-3.01,-2.15,-0.62,-0.52;BONE,143B,1.25,-1.04,0;BONE,CAL72,1.26,-0.23,0;BONE,HOS,0.95,-1.84,0;BONE,HUO3N1,1.19,-1.2,0;BONE,HUO9,1.11,-0.39,0;BONE,MG63,1.15,-1.13,0;BONE,NOS1,0.79,-0.35,0;BONE,NY,1.01,-0.13,0;BONE,SAOS2,1.09,-1.04,0;BONE,SJSA1,0.94,-0.1,0;BONE,U2OS,0.7,-0.3,0;BONE,G292,2.07,-0.52,1;BREAST,BT20,0.79,-0.39,0;BREAST,BT549,0.86,0.47,0;BREAST,CAL120,0.81,-2.79,0;BREAST,CAL51,0.69,0.24,0;BREAST,CAMA1,0.98,-1.01,0;BREAST,DU4475,0.68,0.53,0;BREAST,HCC1954,0.79,-0.44,0;BREAST,HCC202,1.28,0.18,0;BREAST,HCC38,1.13,0.79,0;BREAST,HCC70,1.17,-0.5,0;BREAST,HS578T,1.07,0.19,0;BREAST,MCF7,1.2,0.47,0;BREAST,MDAMB157,0.88,0.44,0;BREAST,MDAMB231,1.27,-1.71,0;BREAST,MDAMB436,1.25,0.49,0;BREAST,MDAMB453,0.92,-2.02,0;BREAST,MFM223,0.94,-0.6,0;BREAST,T47D,1.32,-0.63,0;BREAST,ZR7530,0.68,-0.03,0;BREAST,BT474,1.98,-2.15,1;BREAST,JIMT1,1.92,-7.38,1;LUNG,A427,1.25,-2.93,0;LUNG,A549,1.19,-3.52,0;LUNG,BEN,0.7,-0.72,0;LUNG,H1299,0.68,-1.67,0;LUNG,H1650,1.26,-1.14,0;LUNG,H1838,1.31,-0.26,0;LUNG,H1975,1.22,-0.22,0;LUNG,H2228,1.11,0.34,0;LUNG,H23,1.14,-0.25,0;LUNG,H2342,1.07,-1.99,0;LUNG,H292,1.28,-1.18,0;LUNG,H358,0.99,-0.87,0;LUNG,H460,1.22,-0.42,0;LUNG,H727,1.22,-1.9,0;LUNG,H1793,1.75,-3.01,1;HEADNECK,PCI30,1.16,-0.58,0;PANCREAS,ASPC1,0.92,-0.47,0;PANCREAS,BXPC3,1.17,-0.62,0;PANCREAS,MIAPACA2,1.02,-3.54,0;CERVICAL,C33A,1.33,-1.83,0;CERVICAL,CASKI,0.78,-0.6,0;CERVICAL,HELA,0.94,-0.83,0;CERVICAL,SIHA,0.79,-1.16,0;OVARY,CAOV3,1.25,1.28,0;OVARY,ES2,1.33,-0.08,0;OVARY,OAW42,1.11,-0.15,0;OVARY,OV90,0.76,-0.83,0;OVARY,OVISE,1.14,-2.46,0;OVARY,OVMANA,1.24,0.9,0;OVARY,OVTOKO,1.2,-0.76,0;OVARY,RMGI,1.24,-0.14,0;OVARY,SKOV3,1.31,-0.38,0;OVARY,TOV112D,1.07,-1.3,0;OVARY,TOV21G,0.8,-1.43,0;OESOPHAGUS,ESO26,1.06,0.78,0;OESOPHAGUS,FLO1,1.32,-1.12,0;OESOPHAGUS,OE19,0.92,-0.38,0;OESOPHAGUS,OE33,1.31,-1.09,0;OESOPHAGUS,SKGT4,1.21,0.9,0;OESOPHAGUS,TE1,0.72,0.02,0;OESOPHAGUS,TE10,1.3,-0.67,0;OESOPHAGUS,TE11,0.81,0.68,0;OESOPHAGUS,TE6,0.99,0.68,0;OESOPHAGUS,TE9,0.68,-5.88,0;OESOPHAGUS,TE8,1.7,-0.62,1;ENDOMETRIUM,MFE296,1.3,-2.57,0;CENTRAL_NERVOUS_SYSTEM,KNS42,1.08,-0.84,0";

//var driver = "ERBB2", target="MAP2K3", wilcox_p = "4 x 10<sup>-4</sup>", effect_size = "81%", zdelta_score="-1.145", histotype="Pan cancer", study="Campbell(2016)";

var svg_fancybox_loaded = false;
var drawing_svg = false;
var boxplot_csv = ''; 
// global for now.

// = "79,-5,2,-2.66,-1.28,-0.62,0.04,1.26,-4.61,-3.555,-1.765,-0.91,-0.62;BONE,143B,-0.21,0;BONE,CAL72,-0.61,0;BONE,G292,-1.85,0;BONE,HOS,-2.15,0;BONE,HUO3N1,-1.12,0;BONE,HUO9,-0.91,0;BONE,MG63,-1.48,0;BONE,NOS1,-0.99,0;BONE,NY,0.18,0;BONE,SAOS2,-0.91,0;BONE,SJSA1,0.88,0;BONE,U2OS,0.36,0;BREAST,BT20,-2.29,0;BREAST,BT549,-1.67,0;BREAST,CAL120,1.26,0;BREAST,CAL51,-0.67,0;BREAST,CAMA1,1.04,0;BREAST,DU4475,0.22,0;BREAST,HCC38,-0.23,0;BREAST,HCC70,-0.91,0;BREAST,HS578T,-2.03,0;BREAST,MCF7,-0.42,0;BREAST,MDAMB157,-1.54,0;BREAST,MDAMB231,-0.1,0;BREAST,MDAMB436,-0.1,0;BREAST,MFM223,-1.94,0;BREAST,T47D,-2.31,0;BREAST,BT474,-3.45,1;BREAST,HCC1954,-0.62,1;BREAST,HCC202,-4.61,1;BREAST,JIMT1,-1.09,1;BREAST,MDAMB453,-0.71,1;BREAST,ZR7530,-3.66,1;LUNG,A427,-0.31,0;LUNG,A549,-0.85,0;LUNG,BEN,-1.27,0;LUNG,H1299,0.19,0;LUNG,H1650,0.4,0;LUNG,H1838,-0.34,0;LUNG,H1975,-0.52,0;LUNG,H2228,-0.65,0;LUNG,H23,-0.55,0;LUNG,H2342,-2.66,0;LUNG,H292,-0.54,0;LUNG,H358,0.46,0;LUNG,H460,0.19,0;LUNG,H727,-0.75,0;HEADNECK,PCI30,-0.08,0;PANCREAS,ASPC1,-0.4,0;PANCREAS,BXPC3,-1.26,0;PANCREAS,MIAPACA2,-0.22,0;CERVICAL,C33A,-1.29,0;CERVICAL,CASKI,-1.52,0;CERVICAL,HELA,-1.02,0;CERVICAL,SIHA,-1.49,0;OVARY,CAOV3,0.36,0;OVARY,ES2,-1.13,0;OVARY,OAW42,-2.26,0;OVARY,OV90,-0.3,0;OVARY,OVISE,-1.67,0;OVARY,OVMANA,-1.58,0;OVARY,OVTOKO,-1.32,0;OVARY,TOV112D,0.53,0;OVARY,TOV21G,0.23,0;OVARY,RMGI,-1.55,1;OVARY,SKOV3,-2.49,1;OESOPHAGUS,FLO1,-1,0;OESOPHAGUS,SKGT4,0.61,0;OESOPHAGUS,TE1,-0.81,0;OESOPHAGUS,TE10,-0.82,0;OESOPHAGUS,TE11,0.08,0;OESOPHAGUS,TE8,-0.62,0;OESOPHAGUS,TE9,0,0;OESOPHAGUS,ESO26,-4.29,1;OESOPHAGUS,OE19,-0.83,1;OESOPHAGUS,OE33,-1.98,1;OESOPHAGUS,TE6,-0.99,1;ENDOMETRIUM,MFE296,0.6,0;CENTRAL_NERVOUS_SYSTEM,KNS42,0.37,0"

var irange=0, iwtbox=3, imubox=8;
var itissue=0, icellline=1, iy=2, imutant=3;  // was: ix=2, 
var svgNS="http://www.w3.org/2000/svg"; // Name space needed for SVG.
var svgWidth=500, svgHeight=500;
var XscreenMin=50,  XscreenMax=(svgWidth-10); // To allow for a margin of 50px at left, and 10px at right
var YscreenMin=(svgHeight-50), YscreenMax=10; // To allow a margin of 50px at bottom, and small 10px margin at top
var wtxc=1.6, muxc=3.8, boxwidth=1.8;
var svg, xscale, yscale, Yscreen0, lines;
var tissue_lists;
var cellline_count;
var collusionTestRadius=4.6;
var wt_boxplot_elems, mu_boxplot_elems;

// Array indexes for the 7 number boxplot_stats():
var ilowerwisker=1, ilowerhinge=2, imedian=3, iupperhinge=4, iupperwhisker=5;
  
//$(function() { // on dom ready
   // draw_svg_boxplot(); // but need to wait until AJAX call returns from server with the coordinates for plotting.
//}); // on dom ready

    
function draw_svg_boxplot(driver, target) {

  if ((drawing_svg) || (boxplot_csv=='') || (!svg_fancybox_loaded)) {return true;} // returning 'true' so fancybox will display its content
  drawing_svg = true; // To prevent drawing twice if both callback happened as same time.

  wt_boxplot_elems=[];
  mu_boxplot_elems=[];
  
//console.log("DRAWING SVG****");
  lines = boxplot_csv.split(";"); // 'lines' is global as is used by the tooltip on hoover
  var col = lines[0].split(","); // y-axis range and wt & mu boxes
  
  cellline_count = parseInt(col[0]); // is global variable. // .split(",")[1]
  // The "cellline_count" is the number of cell_lines. So add 1 lines for first line(cellline_count,range,wt_box,mu_box).
  
  if (lines.length-1 != cellline_count) {alert( "Boxplot data length mismatch: "+(lines.length-1)+" != "+cellline_count )}

  var ymin = parseInt(col[1]), ymax = parseInt(col[2]);

  // These are global:
  // From: http://www.i-programmer.info/programming/graphics-and-imaging/3254-svg-javascript-and-the-dom.html
  svg=document.getElementById("mysvg"); // or can create with js: var svg=document.createElementNS(svgNS,"svg"); svg.width=300; svg.height=300; document.body.appendChild(svg);
  
    
  xscale = 100; 
  yscale = (YscreenMax-YscreenMin)/(ymax-ymin);  // This is -ive, so Yscreen0 = YscreenMin + ymin*yscale
  Yscreen0 = YscreenMin - ymin*yscale;  // is really Yscreen0 = YscreenMin + (y0 - ymin)*yscale; eg. 380+(0-2)*(-30)
 
  axes(wtxc,muxc, ymin,ymax, driver,target);

  // To match my javascript boxplot_stats() which return 7 numbers, starting at position 1 (as zero should be the lowest extreme point)   
  var wt_boxstats = []; for (var i=0; i<5; i++) {wt_boxstats[i+1] = parseFloat(col[iwtbox+i]);}
  var mu_boxstats = []; for (var i=0; i<5; i++) {mu_boxstats[i+1] = parseFloat(col[imubox+i]);}
    
  // Store the boxplot lines and rectangle in global array, so can adjust position later:
  wt_boxplot_elems = boxplot( wtxc, boxwidth, wt_boxstats, wt_boxplot_elems);
  mu_boxplot_elems = boxplot( muxc, boxwidth, mu_boxstats, mu_boxplot_elems);
  // **** An idea is variable width is proportional to square root of size of groups: https://en.wikipedia.org/wiki/Box_plot
  // https://stat.ethz.ch/R-manual/R-devel/library/graphics/html/boxplot.html
  // range = this determines how far the plot whiskers extend out from the box. If range is positive, the whiskers extend to the most extreme data point which is no more than range times the interquartile range from the box. A value of zero causes the whiskers to extend to the data extremes.
  // width = a vector giving the relative widths of the boxes making up the plot.
  // varwidth = if varwidth is TRUE, the boxes are drawn with widths proportional to the square-roots of the number of observations in the groups.
  // notch = if notch is TRUE, a notch is drawn in each side of the boxes. If the notches of two plots do not overlap this is ‘strong evidence’ that the two medians differ (Chambers et al, 1983, p. 62). See boxplot.stats for the calculations used.

  line(XscreenMin/xscale,-2, XscreenMax/xscale,-2, "1px", true, "red"); // the red y=-2 full-width line
	
  beeswarm(lines, wtxc-1*boxwidth, muxc-2*boxwidth, boxwidth); // The -1 and -2 are because that is the position set in R for the jitter.
  
  add_tooltips();
}

function tohalf(x, strokewidth) {
  // As drawing vertical or horizontal one-pixel-wide lines positioned at the half pixel will make them exactly one pixel wide and won't be anti-aliased.
  //return x;
  return (strokewidth % 2 == 0) ? Math.round(x) : Math.floor(x)+0.5; // if even widthy then center line on grid, else center half-way between grid lines.
  }


function axes(wtxc,muxc, ymin,ymax, driver, target) {
    line(wtxc, ymin, muxc, ymin, "1px", false, "black"); // the horizontal axis
	
	line(wtxc, ymin, wtxc, ymin+8/yscale, "1px", false, "black"); // tick mark at 'wt'
	line(muxc, ymin, muxc, ymin+8/yscale, "1px", false, "black"); // tick mark at 'mutant'

    // The svg text class is set to: text-anchor: middle.
    text(wtxc,ymin+23/yscale,18,false,"wt");
	
    text(muxc,ymin+23/yscale,18,false,"altered");

    text(0.5*(XscreenMin+XscreenMax)/xscale,ymin+45/yscale,20,false,driver+"  status");
		
	line(XscreenMin/xscale, ymin, XscreenMin/xscale, ymax, "1px", false, "black"); // y-axis	
	for (var y=ymin; y<=ymax; y++) {
	  line((XscreenMin-5)/xscale,y, XscreenMin/xscale,y,"1px",false,"black")
	  var x = y>=0 ? 0.32 : 0.27;
	  text(x,y+8/yscale,18,false, y.toString());
	  }
		
	//text(15/xscale,ymin+2,20,true,target+" Z-score");
    text(15/xscale,0.5*(ymin+ymax),20,true,target+" Z-score");	
    }

function mouseOver(e) {
    // http://stackoverflow.com/questions/12043504/how-to-apply-hover-on-svg-inner-rect-element
	// http://www.petercollingridge.co.uk/data-visualisation/mouseover-effects-svgs
	// http://www.petercollingridge.co.uk/data-visualisation/svg-mouseover-tricks
	// http://www.petercollingridge.co.uk/interactive-svg-components/tooltip
	
    //this.setAttribute("r", "10");	
	//alert("In");
	e = e || window.event;  // Need: window.event for IE <=8 
	var target = e.target || e.srcElement;	
	target.setAttribute("r", "10");
	// $('#title').tooltip( "open" );
	//$( document ).tooltip("open");
	//console.log("Here...");
    }

function mouseOut(e) {
    //this.setAttribute("r", "5");
	//alert("Out");	
	e = e || window.event;  // Need: window.event for IE <=8 
	var target = e.target || e.srcElement;	
	target.setAttribute("r", "5");	
    }

function search_rows_above_and_below(which_row,row,row_above,row_below,row_twoabove,row_twobelow) {
    var i = row.length; // ie. beyond end of this row
    while ( ((i < row_above.length) && row_above[i]) // testing for a space in the row below
         || ((i < row_below.length) && row_below[i]) // and for a space in the row above
         || ((i < row_twoabove.length) && row_twoabove[i]) // testing for a space in the row below
         || ((i < row_twobelow.length) && row_twobelow[i]) // and for a space in the row above		 
        ) {
        i++;
        //console.log('searching_above_and_below '+which_row+': '+i)
        }
    return i;
}

function get_median(y,start,end) {
	var len = end-start+1;
	//console.log("get_median:",start,end,"len:",len);
    if (len==0) {alert("Array is empty"); return;}
	if (len % 2 !=0) { // is odd length
	    return y[start + (len-1)/2];  // or (start+end)/2
	}
	else { // is even length
	    return 0.5*(y[start + (len-2)/2] + y[start + len/2]); // or y[(start+end-1)/2] + y[(start+end+1)/2]
	}
}
 
function boxplot_stats(y) {
// for an array of input numbers (integers or floating point), returns an array of 7 numbers for:
// min, 1.5min, quartile, median, quartile, 1.5max, max
// similar to R's boxplot.stats function.
// see: https://en.wikipedia.org/wiki/Box_plot#Types_of_box_plots
// or the lowest datum still within 1.5 IQR of the lower quartile, and the highest datum still within 1.5 IQR of the upper quartile (often called the Tukey boxplot)[2][3] (as in figure 3)
// https://en.wikipedia.org/wiki/Five-number_summary#Example_in_R
// http://www.ibm.com/support/knowledgecenter/SSLVMB_20.0.0/com.ibm.spss.statistics.help/alg_examine_tukey.htm

// http://mathforum.org/library/drmath/view/60969.html

// Or better: http://peltiertech.com/hinges/
// http://peltiertech.com/comparison/

    var len = y.length;
    // if (len==0) {return [];} // return empty array as no data.
    if (len==0) {return [0,0,0,0,0,0,0];} // or return all zeros.	
	
	console.log("boxplot_stats y: len=",y.length,"   positions:",y);
	
	var sorted = y.sort(function(a, b){return a-b}); // by default sort comapres as strings, so need this compare function parameter.
    //var n = sorted.length;
	var end = len-1;  // as zero-based arrays. Was 'last'
	var min = sorted[0];
	var max = sorted[end];
	
	// Median position: ((n+1)/2 -1) = ((last+2)/2 -1) = ((last+2-2)/2) = last/2
	//var len_is_odd = (last %2 == 0);  // same as: len %2 != 0
    //var median = len_is_odd ? sorted[last/2] : 0.5*(sorted[(last-1)/2] + sorted[(last+1)/2]);

	// Now find the lower and upper "hinges" for Tukey (ie. inclusive Hinge) method:
	var median = get_median(y,0,end);
	if (len %2 != 0) { // odd len, so include the middle in both halves
	   var middle = end/2;
	   var lower_quartile = get_median(y,0,middle);
	   var upper_quartile = get_median(y,middle,end);
	}
    else {
	   var end_of_lower_half = (len-2)/2;
	   var start_of_upper_half = len/2;
	   
	   var lower_quartile = get_median(y,0,end_of_lower_half);
	   var upper_quartile = get_median(y,start_of_upper_half,end);
	}
	
	  // odd: same as (len/2)-0.5. eg. for 10,20,30: we want index (2)/1 = 1 as zero-based arrays, so 20.
      // even: eg. for 10,20,30,40 so (3-1)/2=index 1, and (3+1)/2 = index 2, so 0.5*(20+30)

	// Lower quartile pos: ((n+1)/4 -1) = ((last+2)/4 -1) = ((last+2-4)/4) = ((last-2)/4)
    // Upper quartile pos: (3*(n+1)/4 -1) = (3*(last+2)/4 -1) = (3*last+6-4)/4) = ((3*last+2)/4)
	// eg: 1,2,3,4,5,6,7,8,9,10,11, so quartiles 3,9, ie. zero-based pos 2 and 8.
	
	// or other ways: https://en.wikipedia.org/wiki/Quartile, eg: "Tukey's hinges
	// Method 2:
    //  - Use the median to divide the ordered data set into two halves.
    //  - If there are an odd number of data points in the original ordered data set, include the median (the central value in the ordered list) in both halves.
    //  - If there are an even number of data points in the original ordered data set, split this data set exactly in half.
    //  - The lower quartile value is the median of the lower half of the data. The upper quartile value is the median of the upper half of the data.
    //  - The values found by this method are also known as "Tukey's hinges".
	/*
	if (len_is_odd) { // then include the median in both sets:		
	    var half_len_is_odd = ((last-2) % 4 == 0); // ie. the median position. Same as (last % 4 != 0)
        if (half_len_pos_is_odd) {
           var lower_quartile = sorted[last/4];
           var upper_quartile = sorted[3*last/4];
		}
		else {
           var lower_quartile = 0.5*(sorted[(last-2)/4] + sorted[(last+2)/4]);
           var upper_quartile = 0.5*(sorted[(3*last-2)/4] + sorted[(3*last+2)/4]);
		}
	}
    else { // is even length overall, so split into two halves.
	    var half_len_is_odd = ((last-3) % 4 == 0); // ie. the median position. Same as ((last-1) % 4 != 0)
        if (half_len_pos_is_odd) {
           var lower_quartile = sorted[last/4];
           var upper_quartile = sorted[3*last/4];
		}
		else {
           var lower_quartile = 0.5*(sorted[(last-2)/4] + sorted[(last+2)/4]);
           var upper_quartile = 0.5*(sorted[(3*last-2)/4] + sorted[(3*last+2)/4]);
		}

	// Use floor() and ceiling() or subtract the modulus result: (last-2) % 4
	   var mod = (last-2) % 4;
       var iq = (last-2-mod)/4;
	console.log("Lower mod:"+mod+" iq:"+iq);
       var lower_quartile = 0.5*(sorted[iq] + sorted[iq+1]);
       // var lower_quartile = 0.5*(sorted[Math.floor(iq)] + sorted[Math.ceil(iq)]);
       mod = (3*last+2) % 4;  // will be the reverse of mod above - ie. mirror image (ie. (4-mod_above)
       iq = (3*last+2-mod)/4;
	   // iq = (3*last+2+mod)/4; // if use the above mod, then: var upper_quartile = 0.5*(sorted[iq-1] + sorted[iq]);
	console.log("Upper mod:"+mod+" iq:"+iq);	 
       var upper_quartile = 0.5*(sorted[iq] + sorted[iq+1]);
       // var upper_quartile = 0.5*(sorted[Math.floor(iq)] + sorted[Math.ceil(iq)]);	   
	}
	*/
	
	var quartile_range_15 = 1.5*(upper_quartile - lower_quartile); // as fences are within (1.5 of interquartile range) from the lower and upper quartiles respectively.
    var lower_fence = (lower_quartile-quartile_range_15);
    for (var i=0; i<=end; i++) {
		if (sorted[i]>=lower_fence) {lower_fence=sorted[i]; break}
	}
    var upper_fence = (upper_quartile+quartile_range_15);
    for (var i=end; i>=0; i--) {
		if (sorted[i]<=upper_fence) {upper_fence=sorted[i]; break}
	}
	
	// eg: There are eight observations, so the median is the mean of the two middle numbers, (2 + 13)/2 = 7.5. Splitting the observations either side of the median gives two groups of four observations. The median of the first group is the lower or first quartile, and is equal to (0 + 1)/2 = 0.5. The median of the second group is the upper or third quartile, and is equal to (27 + 61)/2 = 44. The smallest and largest observations are 0 and 63.
	console.log("boxplot_stats:",min, "lfence:",lower_fence, "lquart:",lower_quartile, "median:",median, "uquart:",upper_quartile, "ufence:",upper_fence, max );
	
	return [ min, lower_fence, lower_quartile, median, upper_quartile, upper_fence, max ];
}

// Process 3D:
//https://github.com/nylen/d3-process-map

//http://nylen.tv/d3-process-map/graph.php
//http://nylen.tv/d3-process-map/graph.php?dataset=les-mis

//illustrate the relationships between objects in a process using d3.js.

function download_legend(legend_type) {	
  // Using canvas, as IE9+ supports canvas.
  var ytop=20, xcircles=20, rad=8, xtext=40, line_height=25, font="20px Arial";
  // maybe: font-family: sans-serif;
 
  
  var list;
  if (legend_type=='selected') {
    show_message("download_selected_legend", "Downloading...");
    list = tissue_lists;
	//for (tissue in ) {console.log(tissue_colours[tissue], tissue)}
  }
  else if (legend_type == 'all') {
    show_message("download_all_legend", "Downloading...");	  
	list = tissue_colours;	
  }
  
  
  //  http://stackoverflow.com/questions/11816431/how-to-add-a-html5-canvas-within-a-div

  var canvas = document.createElement('canvas');
  canvas.id="mycanvas"; // or:  canvas.setAttribute("id", "mycanvas");
  // <canvas id="myCanvas" width="200" height="100"></canvas>  // Optionally: style="border:1px solid #000000;"  
  //var canvas = document.getElementById('mycanvas');
  
  ctx = canvas.getContext('2d');
  ctx.font = font;
  // var len = Object.keys(list).length; // works in IE9+. 
  // Otherwise: var size = 0, key; for (key in obj) {if (obj.hasOwnProperty(key)) size++;}
  var len=0, maxtextwidth=0, tissue;
  for (tissue in list) {
	 if ((legend_type=='selected') && (!document.getElementById('cb_'+tissue).checked)) {continue}
     var width = ctx.measureText(histotype_display(tissue).replace('&amp;','&')).width;
     if (width>maxtextwidth) {maxtextwidth=width}
	 len++;
     }
    
  canvas.width  = xtext+maxtextwidth+xcircles-rad; // margin of xcircles around
  canvas.height = ytop+(len-1)*line_height+ytop; // so margin of ytop at top and bottom
  //canvas.style="border:1px solid #000000;" is only for display on screen, as downloaded image doesn't have this box. Need to draw a rect.

  // To avoid anti-aliasing, draw lines at half-pixel positions: http://www.rgraph.net/docs/howto-get-crisp-lines-with-no-antialias.html
  canvas_rect(ctx, 0.5,0.5, canvas.width-1, canvas.height-1, "white", "black"); // Make background white inside black rect.
  //canvas_line(ctx, 2.5,20.5,2.5,50.5, "black");
  // can translate the 0,0 position, eg: ctx.translate(radius, radius);
  // For modifying images maybe use:
  //    context.save();
  //    context.restore();
  // ctx.clearRect(...)
  // ctx.globalAlpha=0.2; (0=transparent, 1=opake)
  // function updateClockImage() {
  // snapshotImageElement.src = canvas.toDataURL();   // To paste canvas into an <img> tag.
  // from: http://www.informit.com/articles/article.aspx?p=1903884&seqNum=10
  // To hide shapes in canvas using animate: http://stackoverflow.com/questions/22235313/how-to-hide-an-element-after-drawing-on-canvas-with-settimeout-javascript
  
  var y = ytop;
  for (tissue in list) {	  
	  if ((legend_type=='selected') && (!document.getElementById('cb_'+tissue).checked)) {continue}
	  var mtext = histotype_display(tissue).replace('&amp;','&'); // for "Blood &amp; Lymph"	  
      //console.log(tissue_colours[tissue], mtext); 
	  
	  // Add 0.5 to improve the anti-aliasing of the circle. (Adding 0.5 has no effect on the text)
	  canvas_circle(ctx, xcircles+0.5, y-0.5, rad, tissue_colours[tissue]);
      canvas_text(ctx, xtext, y, mtext, font);
	  y += line_height;	  
	  }

    var filename="Legend_"+legend_type+'_'+len.toString()+'tissues.png';
    download_data(canvas.toDataURL("image/png",1), filename);

//canvas.toDataURL("image/png");
//(defaults to PNG). The returned image is in a resolution of 96 dpi.
//For encoderOptions Optional
//A Number between 0 and 1 indicating image quality if the requested type is image/jpeg or image/webp.
//If this argument is anything else, the default value for image quality is used. The default value is 0.92. Other arguments are ignored.

  return false; // false prevents page refreshing.
}


function canvas_rect(ctx, x,y, width,height, fillcolor, strokecolor) {
  ctx.beginPath();
  ctx.fillStyle = fillcolor;
  ctx.lineWidth = "1";
  ctx.strokeStyle = strokecolor;
  ctx.rect(x,y, width, height);
  ctx.stroke();
  ctx.fill();
  ctx.closePath(); // Circles and rectangles don't actually need the path to be closed.  

  // beginPath(); rect(); fill(); stroke(); closePath(); will have same effect as fillRect; strokeRect():
  //ctx.fillStyle = fillcolor;
  //ctx.lineWidth = "1";
  //ctx.strokeStyle = strokecolor;
  //ctx.strokeRect(x,y, width, height);  // ctx.strokeRect(20,20,150,100);
  //ctx.fillRect(x,y, width, height);  // ctx.strokeRect(20,20,150,100);  
  }

function canvas_line(ctx, x1,y1,x2,y2, color) {
  ctx.lineWidth = "1";
  ctx.strokeStyle = color;
  ctx.moveTo(x1,y1);
  ctx.lineTo(x2,y2);
  ctx.stroke();  // This actually draws the line.
  }

function canvas_circle(ctx, x, y, r, fillcolor) {
  ctx.beginPath();  // Beginning new shape
  ctx.arc(x, y, r, 0, 2 * Math.PI); // false); // params: xcentre, ycentre, radius, startAngle, endAngle, anticlockwise(optional);
  ctx.fillStyle = fillcolor; // OR: = 'rgba(255,255,255,0.8)';
  ctx.fill();
  ctx.lineWidth = 1;
  ctx.strokeStyle = "black";
  ctx.stroke();
  ctx.closePath(); // Circles and rectangles don't actually need the path to be closed.
  }

function canvas_text(ctx, x,y, mtext, font) {
  ctx.font = font; // eg: "15px Arial", or "30px Comic Sans MS"; or ctx.font = radius*0.15 + "px arial";
  ctx.fillStyle = "black";
  // ctx.textAlign = "center";
  ctx.textBaseline="middle";
  ctx.fillText(mtext,x,y); // eg: ctx.fillText("Hello World", canvas.width/2, canvas.height/2); 
  }

  
/* or:
     <style>
        #canvas {
           display: none;
        }

        #snapshotImageElement {
           position: absolute;
           left: 10px;
           margin: 20px;
           border: thin solid #aaaaaa;
        }
*/




function beeswarm(lines,wtx,mux,boxwidth) {
// A beeswarm with jitter example: http://jsfiddle.net/5kc0wtfg/5/

// Test examples from: https://en.wikipedia.org/wiki/Quartile
console.log(boxplot_stats([6, 7, 15, 36, 39, 40, 41, 42, 43, 47, 49])); // quartiles: 25.5, 40, 42.5
console.log(boxplot_stats([7, 15, 36, 39, 40, 41])); // quartiles: 15, 37.5,40
console.log(boxplot_stats([1]));

  tissue_lists = {}; // a global variable as used by 'toggle_tissue_checkboxes(e)'
var wt_points=[],mu_points=[];
  var wtHorizPointSpacing = 8, muHorizPointSpacing = 12;  // was 12 for horizontal point spacing, but ERBB2 vs ERBB2 points overflow the boxplot width
  var tissue_count=0;
  var wtleft=[], wtright=[], muleft=[], muright=[]; // To avoid overlapping points.
  var wt_tissue_counts = {}, mu_tissue_counts = {};
  var NA_total = 0; // count of lines with y='NA'
  
  for (var i=1; i<lines.length; i++) { // corectly starts at i=1, as lines[0] is the boxplot dimensions.
    var col = lines[i].split(",");
    var tissue = col[itissue];
	if (tissue=="BONE") {tissue="OSTEOSARCOMA"; col[itissue]=tissue; lines[i]=col.join(',');} // BONE is "OSTEOSARCOMA" in the tissue_colours array.

	var isWT = col[imutant]=="0";  // Wildtype rather than mutant.
	
    if (col[iy]=='NA') {console.log("Skipping "+col[icellline]+" "+tissue+" as y='"+col[iy]+"'"); NA_total++; continue;}

if (isWT) {wt_points.push(parseFloat(col[iy]))}
else {mu_points.push(parseFloat(col[iy]))}

    var y = tohalf(Yscreen0 + parseFloat(col[iy]) * yscale, 1);
    var Yi = Math.round(y / collusionTestRadius); // 5 is twice the circle radius.
  
    var e = document.createElementNS(svgNS,"circle");

	var colour = tissue_colours[tissue];
	if (typeof colour === 'undefined') {alert("Unexpected tissue '"+tissue+"'");}
	
    e.setAttribute("fill", colour);
    //e.setAttribute("stroke", colour);    // e.style.stroke=colour;
	// e.setAttribute("stroke-width", "1"); // e.style.strokewidth=1;
	// e.setAttribute("fill-opacity", "0.5");

	var x = isWT ? (wtx+boxwidth)*xscale : (mux+2*boxwidth)*xscale;  // The centerline.
		
//	newFilledArray(len, val) {
//    var a = [];
//    while(len--){
//    	a.push(val);
//    }
//    return a;
//}

    if (tissue in tissue_lists) {tissue_lists[tissue].push(e);}
	else {
	  tissue_lists[tissue]=[e];
	  wt_tissue_counts[tissue]=0;
	  mu_tissue_counts[tissue]=0;
	  tissue_count++;
	  }
	if (col[imutant]==0) {wt_tissue_counts[tissue]++}  // This is correctly outside the above
	else {mu_tissue_counts[tissue]++}

	if (isWT) { // Wild type
//console.log("isWT: y:"+y+" Yi:"+Yi);
	    // right is set to one true so won't plot two points on centre line.
		for (var j=-2; j<=2; j++) {
	      if (typeof wtleft[Yi+j] === 'undefined') {if (typeof wtright[Yi+j] !== 'undefined') {alert("wtright defined Yi+'+j+' "+Yi)}; wtleft[Yi+j]=[]; wtright[Yi+j]=[true];}
		  }
		  // console.log('wtleft['+j+']=[]');
				
// find position on left nearest to centre line:

	   var xleft  = search_rows_above_and_below('wtleft:'+Yi,wtleft[Yi],wtleft[Yi-1],wtleft[Yi+1],wtleft[Yi-2],wtleft[Yi+2]);
	   var xright = search_rows_above_and_below('wtright:'+Yi,wtright[Yi],wtright[Yi-1],wtright[Yi+1],wtright[Yi-2],wtright[Yi+2]);

//       var xleft = wtleft[Yi].length; // eg '0' initially	   
//	   while ( ((xleft<wtleft[Yi-1].length) && wtleft[Yi-1][xleft]) // testing for a space in the row below
//	        || ((xleft<wtleft[Yi+1].length) && wtleft[Yi+1][xleft]) // and for a space in the row above
//			) {xleft++; console.log('Finding xleft: '+xleft)}

//       var xright = wtright[Yi].length; // eg '1' initially
//	   while ( ((xright<wtright[Yi-1].length) && wtright[Yi-1][xright])
//	        || ((xright<wtright[Yi+1].length) && wtright[Yi+1][xright])
//			) {xright++; console.log('Finding xright: '+xright)}

//       if (tissue_count % 2 == 0) // put odd numbered tissues on the left, even on right.
	   if (xleft<=xright)
	     {for (var j=wtleft[Yi].length; j<xleft; j++) {wtleft[Yi][j]=false;}; wtleft[Yi][xleft]=true; x-=xleft*wtHorizPointSpacing;} // console.log('using xleft x='+x+' wtleft[Yi].length:'+wtleft[Yi].length);
	   else 
	     {for (var j=wtright[Yi].length; j<xright; j++) {wtright[Yi][j]=false;}; wtright[Yi][xright]=true; x+=xright*wtHorizPointSpacing;} // console.log('using xright x='+x+' wtright[Yi].length:'+wtright[Yi].length);
	   
// return; // as run away script maybe ?
	   
// ** Worth trying:  https://github.com/gillyb/reimg
// Just include this library in your html code: in header include   script src="reimg.js" 
// Here are some examples on how to use it:
// convert svg element to img element:  var img = ReImg.fromSvg(document.querySelector('svg')).toImg();  // now 'img' is the img element created
// convert svg element to png:  var png = ReImg.fromSvg(document.getElementById('svg-element-id')).toPng();
// force client download of svg as png image:   ReImg.fromSvg(document.querySelector('svg')).downloadPng();
// convert canvas to png:   var png = ReImg.fromCanvas(document.getElementById('canvasId')).toPng();

// I created a small library that does this (along with some other handy conversions). It's called reimg, and it's really simple to use.
// ReImg.fromCanvas(yourCanvasElement).toPng()
/*
==
function downloadImage()
            {
                var canvas = document.getElementById("thecanvas");
                var image = canvas.toDataURL();

                var aLink = document.createElement('a');
                var evt = document.createEvent("HTMLEvents");
                evt.initEvent("click");
                aLink.download = 'image.png';
                aLink.href = image;
                aLink.dispatchEvent(evt);
            }


body onload="draw()"
    <canvas width=200 height=200 id="thecanvas"></canvas>
    <div><button onclick="downloadImage()">Download</button></div>
    <image id="theimage"></image>

BUT IE 8+ only support "data: for img, link, css
Converting an nsIFile to a data URIEDIT
This function returns a base 64-encoded data URI from the passed nsIFile.

function generateDataURI(file) {
  var contentType = Components.classes["@mozilla.org/mime;1"]
                              .getService(Components.interfaces.nsIMIMEService)
                              .getTypeFromFile(file);
  var inputStream = Components.classes["@mozilla.org/network/file-input-stream;1"]
                              .createInstance(Components.interfaces.nsIFileInputStream);
  inputStream.init(file, 0x01, 0600, 0);
  var stream = Components.classes["@mozilla.org/binaryinputstream;1"]
                         .createInstance(Components.interfaces.nsIBinaryInputStream);
  stream.setInputStream(inputStream);
  var encoded = btoa(stream.readBytes(stream.available()));
  return "data:" + contentType + ";base64," + encoded;
}
	
*/

/*	   
	   if ( > wtright[Yi]) { // plot a point on the right:
		  var Xi = Math.max(wtright[Yi],wtright[Yi-1],wtright[Yi+1]);
		  x+=Xi*12;
		  wtright[Yi]=Xi+1;
		  console.log("right:",Yi,Xi,x,wtright[Yi]);
		 } 
	   else { // plot a point on the left:
	   	  var Xi = Math.max(wtleft[Yi],wtleft[Yi-1],wtleft[Yi+1]);
		  x-=Xi*12;
		  wtleft[Yi]=Xi+1;
		  console.log("left:",Yi,Xi,x,wtleft[Yi]);		  
//	   x-=wtleft[Yi]*12; wtleft[Yi]++	   
	     }
*/
	   }
	else { // is Mutant
	  for (var j=-2; j<=2; j++) {
	    if (typeof muleft[Yi+j] === 'undefined') {if (typeof muright[Yi+j] !== 'undefined') {alert("muright defined Yi+'+j+' "+Yi)}; muleft[Yi+j]=[]; muright[Yi+j]=[true];}
	  }
      // console.log('muleft[0]=[]'); 
	  
// find position on left nearest to centre line:
		
	   var xleft  = search_rows_above_and_below('muleft:'+Yi,muleft[Yi],muleft[Yi-1],muleft[Yi+1],muleft[Yi-2],muleft[Yi+2]);
	   var xright = search_rows_above_and_below('muright:'+Yi,muright[Yi],muright[Yi-1],muright[Yi+1],muright[Yi-2],muright[Yi+2]);

//       if (tissue_count % 2 == 0) // put odd numbered tissues on the left, even on right.	   
	   if (xleft<=xright)
	     {for (var j=muleft[Yi].length; j<xleft; j++) {muleft[Yi][j]=false;}; muleft[Yi][xleft]=true; x-=xleft*muHorizPointSpacing;} // console.log('using xleft x='+x+' muleft[Yi].length:'+muleft[Yi].length);
	   else 
	     {for (var j=muright[Yi].length; j<xright; j++) {muright[Yi][j]=false;}; muright[Yi][xright]=true; x+=xright*muHorizPointSpacing;} // console.log('using xright x='+x+' muright[Yi].length:'+muright[Yi].length);
	   
		}
	
	
//	console.log('undefined',wtleft[5]);}
	
	//e.setAttribute("cx", tohalf((xcenter + boxwidth*parseFloat(col[ix])) * xscale, 1).toString() ); // or: e.cx.baseVal.value =  parseFloat(col[2]) * xscale );
	// was: (xcenter + boxwidth*parseFloat(col[ix])
	
	//alert('Add wrapping of x if exceeds the width of the boxplot')
    // .... but might be a space on the right or left of centre lines.
	
	//if (x < -0.5*boxwidth*xscale ...xcentre ....) {
    //if (x >  0.5*boxwidth*xscale) { 6 is half the width .... but need to remove the mod of boxwidth/12

	//add the xcentre after the above calculations 
	
	e.setAttribute("cx", tohalf(x, 1).toString() ); // or: e.cx.baseVal.value =  parseFloat(col[2]) * xscale );
	
	e.setAttribute("cy", y.toString() ); // or: e.cy.baseVal.value = parseFloat(col[3]) * yscale );
		
	e.setAttribute("r", "5"); // Firefox and IE don't use the 'r' in the 'circle' class (whereas Chrome does)  e.r.baseVal.value = "5"; set in the 'circle' class
	var id = "c"+i.toString();
	e.setAttribute("id", id); // 'c' for circle or cell_line
	
	//e.setAttribute("onmouseover", "mouseOver();");
    //e.setAttribute("onmouseout", "mouseOut();"); // ="evt.target.setAttribute('opacity','1)');"/>
	e.onmouseover = mouseOver;  // or: e.onmouseover = function() { myFun(this) };
	// the mouseenter event, the mouseover event triggers if a mouse pointer enters any child elements as well as the selected element. The mouseenter event is only triggered when the mouse pointer enters the selected element. 
	e.onmouseout = mouseOut;
	
	//evt.target.setAttribute('opacity', '0.5');"
	svg.appendChild(e);
	//console.log(i,((xcenter + parseFloat(col[ix])) * xscale).toString(),(Yscreen0 + parseFloat(col[iy]) * yscale).toString());
    }
		
	//var legend_thead = '<thead><tr><th>Show<br/>"+toggle_button+"</th><th>Tissue</th><th>Total<br/>cell lines</th><th>WildType<br/>cell lines</th><th>Altered<br/>cell lines</th></tr></thead>';
	
	var legend_thead = '<thead><tr><th rowspan="2">Show</th><th rowspan="2">Tissue</th><th colspan="3">Cell lines</th></tr><tr><th>Wild type</th><th>Altered</th><th>Total</th></tr></thead>';
  
	
	var legend_tbody='<tbody>';
	var wt_total=0, mu_total=0;
    for (tissue in tissue_lists) {
	  var colour = tissue_colours[tissue];
	  
//	  $('head').append('<style type="text/css">.'+tissue+'_tooltip{background:'+colour+';}</style>'); // add the style to use later for the tooltips background colour.	  
	  
      if (tissue_lists[tissue].length != wt_tissue_counts[tissue]+mu_tissue_counts[tissue]) {alert("ERROR: Tissue count mismatch for tissue: '"+tissue+"'")} // Just to check my script is working correctly
	  
	  if (wt_tissue_counts[tissue]==0) {wt_tissue_counts[tissue]='<i>'+wt_tissue_counts[tissue].toString()+'</i>'} // To put italics on the zeros
	  else {wt_total+=parseInt(wt_tissue_counts[tissue])}
	  if (mu_tissue_counts[tissue]==0) {mu_tissue_counts[tissue]='<i>'+mu_tissue_counts[tissue].toString()+'</i>'}
	  else {mu_total+=parseInt(mu_tissue_counts[tissue])}
	  
	  legend_tbody += '<tr><td id="td_'+tissue+'" style="background-color:'+colour+'"><input type="checkbox" id="cb_'+tissue+'" checked/></td>'
	   + '<td>'+histotype_display(tissue)+'</td>'
	   + '<td>'+wt_tissue_counts[tissue]+'</td>'
	   + '<td>'+mu_tissue_counts[tissue]+'</td>'
	   + '<td>'+tissue_lists[tissue].length+'</td></tr>';
	  }
    legend_tbody+='</tbody>';


	var all_button = '<input input type="button" id="all_checkboxes" value="All" style="font-size: 90%" onclick="tissue_checkboxes(\'all\');">';
	var none_button = '<input input type="button" id="none_checkboxes" value="None" style="font-size: 90%" onclick="tissue_checkboxes(\'none\');">';
	
    // Disabled the toggle button:
    //var toggle_button = '<br/><input input type="button" id="toggle_checkboxes" value="Toggle" style="font-size: 90%" onclick="tissue_checkboxes(\'toggle\');">';	
    // var legend_tfoot = '<tfoot><tr><td>'+all_button+none_button+toggle_button+'</td>'
	
	var legend_tfoot = '<tfoot><tr><td>'+all_button+none_button+'</td>'
	 + '<td>Totals:</td><td>'+wt_total+'</td>'
	 + '<td>'+mu_total+'</td>'
	 + '<td>'+(wt_total+mu_total)+'</td></tr></tfoot>';
	  // The onchange event should also work with keyboard input, whereas onclick is only mouse clicks I think.

    legend = legend_thead + legend_tbody + legend_tfoot;
		  
	$("#legend_table").html(legend);
	
	if ( (wt_total+mu_total+NA_total) != cellline_count) {alert("cellline_count mismatch: "+(wt_total+mu_total+NA_total)+" != "+cellline_count)}
	
	// The inline onchange="..." tag doesn't pass the event in all browsers, which is needed, so attaching the events using javascript:
    for (tissue in tissue_lists) {
		showhide_cell_clicked
		document.getElementById("td_"+tissue).onclick=showhide_cell_clicked;
		document.getElementById("cb_"+tissue).onchange=showhide_tissue;
		}
		
console.log("rline0:",lines[0]);
var wt_stats=boxplot_stats(wt_points);
var mu_stats=boxplot_stats(mu_points);
//console.log("mystats wt:",wt_stats);
//console.log("mystats mu:",mu_stats);


var minplot=Math.floor(Math.min(wt_stats[0],mu_stats[0])); // [0] is min extreme value in the boxplot_stats
var maxplot=Math.ceil(Math.max(wt_stats[6],mu_stats[6]));  // [6] is max extreme value in the boxplot_stats
//console.log("min,max:",minplot,maxplot);

var mystats=[lines.length-1,minplot,maxplot];
var col=lines[0].split(',');
//if ( (col[0]!=lines.length-1)
//  || (col[1]!=minplot)
//  || (col[2]!=maxplot))
//  {alert("Mismatch in count or min/max: "+(lines.length-1)+" "+minplot+" "+maxplot);}

// a convoluted way to convert to a string with 3 deciimal places without trailing zeros:
// alternative is: http://numeraljs.com/
for (var i=1; i<6; i++) {mystats.push(parseFloat(wt_stats[i].toFixed(3)).toString())}
for (var i=1; i<6; i++) {mystats.push(parseFloat(mu_stats[i].toFixed(3)).toString())}
//console.log("mystats:",mystats);
console.log("jsline0:",mystats.join(","));
//if (mystats.join(",") != lines[0]) {alert("Difference between R and my JS boxplot_stats() functions")}
var msg='';
// As the current R version uses the y valueswith more than 2 decomal places for Achilles/Colt values to compute the boxplot_stats, so just check to 1 decimal place:
for (var i=0; i<=col.length; i++) {if (Math.abs(parseFloat(col[i]-mystats[i])>0.1)) {msq += "Diff "+i+": "+col[i]+" "+mystats[i].toString()}}
if (msg !='') {alert(msg);}


  	// Initialise the Table sorter for the legend_table:
	// Need to add the totals as separate.
/*
Need to fix the column widths (as includes the sort arrow now) and tissue cell colours 
    $("#legend_table").tablesorter({
        // debug: true, // outputs to firebug console
		showProcessing: true,
		theme: 'blue',
//		widgetOptions: {
//			scroller_height: 400,
//			resizable_widths: [ '16%', '12%', '12%', '12%', '12%', '12%', '12%', '12%'], // or use eg: '20px'
//			filter_functions: { .......... // 0-based column indexes:
//			},		
		sortInitialOrder: "asc", // default sort order
		sortRestart: true, // so sort always restarts from the specified sortInitialOrder.
		sortStable: true,
		ignoreCase: true,  // sort ignores case
		filter_ignoreCase: true, // filtering ignores case
	});
*/	
		
}


function add_tooltips() {
    // An alternative tooltips: http://www.mecxpert.de/svg/tooltips.html
  // good: https://forum.jquery.com/topic/tooltip-on-svg-title-element
  // http://stevenbenner.github.io/jquery-powertip/
  // jQuery Tipsy: http://onehackoranother.com/projects/jquery/tipsy/ (these display quickly)
  // Good info about the different types of tooltips for SVG elements.
    // $('#title').tooltip({
  $("#mysvg, #plot_title").tooltip({  // was $(document).tooltip(....
    items: "circle, [data-gene]",
	position: { my: "left+28 center", at: "center center+10" }, // at: "right center" }
	//position: { my: "right-200 center", at: "center center-100" }, // at: "right center" }	
	show: false, //{ effect: "", duration: 0, delay: 0},
	hide: false, // { effect: "", duration: 0, delay: 0}, // see: http://webduos.com/tooltip-using-jquery-ui-library/#.Vvb48uKLSih	
    // tooltipClass: "custom-tooltip-styling", // doesn't work :(
	content: function(callback) {
	  var element = $( this );
	  		//alert("in tooltip "+element.id);
      if ( element.is( "circle" ) ) {
	    var id = element.attr("id");
        var i = parseInt(id.substring(1)); // remove the starting 'c'
	    var col = lines[i].split(",");  // or could encode the tissue and cellline in the ID.
		
     	//var y = tohalf(Yscreen0 + parseFloat(col[iy]) * yscale, 1);
        //var Yi = Math.round(y / collusionTestRadius); // 5 is twice the circle radius.
        var tissue = col[itissue]; // 	if (tissue=="BONE") {tissue="OSTEOSARCOMA"; col[itissue]=tissue; lines[i]=col.join(',');} // BONE is "OSTEOSARCOMA" in the tissue_colours array.
		var mutant = col[imutant];
		// the following is background, not backgroundColor:
//		this.style.background=tissue_colours[tissue];  // eg: element.style.backgroundColor = "red";
//		console.log(this);
//alert(tissue_colours[tissue]+'_tooltip');
       //$( document ).tooltip( "option", "tooltipClass", tissue_colours[tissue]+'_tooltip' );
	   
// setting custom style: http://stackoverflow.com/questions/4780759/overriding-css-styles-of-the-jquery-ui-tooltip-widget
// https://recalll.co/app/?q=overriding%20css%20jquery%20tooltip	   
//  add !important to the end of the lines in your css
// http://stackoverflow.com/questions/15054294/jquery-ui-tooltip-custom-class-on-page-load
// ": Multiple !important class declarations and precedence helped me out: "If the same property is declared in both rules, the conflict is resolved first through specificity, then according to the order of the CSS declarations. The order of classes in the class attribute is not relevant.". So I could solve the problem by first calling the ui-css and then my own css:"
// http://stackoverflow.com/questions/26135451/how-to-change-tooltip-color-on-open-using-jquery-ui-tooltip

// example that works: http://jsfiddle.net/Vg6wP/12/

//	   $("#mysvg").tooltip( "option", "tooltipClass", 'custom-tooltip-styling');
 //alert("Get:"+$( document ).tooltip( "option", "tooltipClass" ));

 // Customising Tooltips: https://blog.udemy.com/jquery-tooltip-example/

// Changing element style with javascript: https://www.w3.org/wiki/Dynamic_style_-_manipulating_CSS_with_JavaScript
//    https://www.kirupa.com/html5/setting_css_styles_using_javascript.htm
 
 // <p style="background-color:'+tissue_colours[tissue]+';"> .... +'</p>'
 
 
        // To add the mutation type, use: +(mutant!="0" ? "MutantType....<br/>" : "")
        return '<b>'+col[icellline]+'</b><br/>'+histotype_display(tissue)+'<br/>Z-score: '+col[iy]; // '<br/>y: '+y+'<br/>Yi: '+Yi+
	    }
      else if ( element.is( "[data-gene]" ) ) { // To display the ncbi_summary for the driver and target genes in the boxplolt_title.
        var gene_name = element.attr("data-gene");  // was: = element.text();
		if (gene_name in gene_info_cache) {
			var result = format_gene_info_for_tooltip(gene_info_cache[gene_name]);
			callback(result);
			}
		else {
            var url = global_url_gene_info_for_mygene.replace('mygene',gene_name);
            $.ajax({
              url: url,
              dataType: 'json', 
            })
            .done(function(data, textStatus, jqXHR) {  // or use .always(...)
              if (data['success']) {
			  	gene_info_cache[gene_name] = data; // cache to retrieve faster next time.
			    result = format_gene_info_for_tooltip(data);
			    callback(result);
				}
			  else {callback("Error: "+data['message'])}
		    })
		    .fail(function(jqXHR, textStatus, errorThrown) {
			  callback("Ajax Failed: '"+textStatus+"'  '"+errorThrown+"'");
            })
		  }
        }
		
	},
	
	// could dynamically create the styles:  $('head').append('<style type="text/css">.novice{color:green;}</style>'); 
	
	// From: http://stackoverflow.com/questions/26135451/how-to-change-tooltip-color-on-open-using-jquery-ui-tooltip
//	 tooltipClass: tissue_colours[tissue]+'_tooltip',  // severity,
//        show: "slideDown",
//        open: function (event, ui) {
//            ui.tooltip.hover(function () {
//                $(this).fadeTo("slow", 0.5);
//            });
//        }
  });
}


function rect(xcenter,width,ystats, e) {
	// A 45 degree rotated square (a diamond) can be created using:
	//  1  <rect x="203" width="200" height="200" style="fill:slategrey; stroke:black; stroke-width:3; -webkit-transform: rotate(45deg);"/>
	//console.log("rect:",typeof e);
    if (typeof e == "undefined") { e = document.createElementNS(svgNS,"rect");  } // console.log("SVGrect made");
	else if (!(e instanceof SVGRectElement)) {alert("rect(): expected 'rect' for existing elem, but got: "+e.tagName)}
		
	e.setAttribute("x", tohalf((xcenter-0.5*width)*xscale, 1) );
	var y = tohalf(Yscreen0 + ystats[iupperhinge]*yscale, 1);
//console.log("*** RECT: ",Yscreen0, ystats[iupperhinge], yscale, y);

	e.setAttribute("y", y);  // Note: box drawn upside down, as screen zero is top left.
    e.setAttribute("width", Math.round(width*xscale) );	
	e.setAttribute("height", Math.round( (Yscreen0+ystats[ilowerhinge]*yscale)-y) );	// yscale is -ive. Slightly more accurate than (ystats[1]-ystats[3])*yscale, as ystats[3]*yscale has been moved slightly by the tohalf.
	//e.setAttribute("fill", "none"); // set by the CSS
	//e.setAttribute("stroke", "black");
	//e.setAttribute("stroke-opacity", "1.0");
	//e.setAttribute("stroke-width", strokewidth);
    svg.appendChild(e); // or: document.documentElement.appendChild(elem);
	return e;
	}
	
function line(x1,y1,x2,y2,strokewidth,dashed,colour, e) {
	//console.log("line:",typeof e);
	if (typeof e == "undefined") { e = document.createElementNS(svgNS,"line"); } // console.log("SVGline made");
    else if (!(e instanceof SVGLineElement)) {alert("line(): expected 'line' for existing elem, but got: "+e.tagName)}	
	
    var isVertical = x1==x2;
    var isHorizontal = y1==y2;
	
	// For sharp lines, best to have position at 0.5 if thinkness is 1px, then won't need antialiasing.
	var x = isVertical ? tohalf(x1*xscale, strokewidth) : x1*xscale;
	e.setAttribute("x1", x);
	e.setAttribute("x2", (isVertical ? x : x2*xscale) );  // otherwise tohalf(x2*xscale) which is same as above.
    //if (isVertical) {console.log("tohalf x"+x2+" => "+x);}

	var y = isHorizontal ? tohalf(Yscreen0 + y1*yscale, strokewidth) : Yscreen0 + y1*yscale;
//console.log("*** line:", Yscreen0, y1, yscale, y);
	e.setAttribute("y1", y);	
	e.setAttribute("y2", (isHorizontal ? y : Yscreen0 + y2*yscale) );
    //if (isHorizontal) {console.log("tohalf y"+y2+" => "+y);}
	
	e.setAttribute("stroke", colour); // as black is default in the CSS
	e.setAttribute("stroke-width", strokewidth);
	if (dashed) {e.setAttribute("stroke-dasharray", "6,3");} // se: http://www.w3schools.com/svg/svg_stroking.asp
    svg.appendChild(e);
	return e;
	}
	
	
function text(x,y,size,vertical,text, e) {
    // Fore attributes, see: http://www.w3schools.com/svg/svg_text.asp
	// if wish to position text better, could first get size using, either:
	// getBBox(text) -> returns x.width and x.height
    // getBoundingClientRect(text) return x.width and x.height, but affected by any scaling in the SVG elements.
    // getComputedTextLength(text) return width }, }, // for text elements only. Very slight difference result from getBBox
  	// see: http://bl.ocks.org/MSCAU/58bba77cdcae42fc2f44
	// Maybe "does not seem to work if the text element is styled using CSS; the calculated pixel width corresponds to the document´s default font size."
	// var el = document.getElementsByTagName('text')[3];  <-- if element created using SVG markup tags, rather than with javascript.
    // el.getComputedTextLength(); // returns a pixel integer

	// You can set the word spacing of a text using the word-spacing CSS property. The word spacing is the amount of white space between the words in the text. Here is an example:

    //<text x="20" y="20">
    //Word spacing is normal
    // </text>
    // <text x="20" y="40"
    //  style="word-spacing: 4;"> (means the number of extra spaces (?pixels) between words.
	// can set style=stroke:none; for not outline around text, just a fill, otherwise looks bold text.
	// in some browsers, can use:  style="writing-mode: tb;" for vertical (top-to-bottom) text instead of rotating text
	// The y-attribute determines where to locate the bottom of the text (not the top)
	// Good: http://tutorials.jenkov.com/svg/text-element.html
	
	// useful: http://www.hongkiat.com/blog/scalable-vector-graphics-text/
	
	// *** Better to position text, could use:  style="text-anchor: middle" so uses text centre for positioning text
	if (typeof e == "undefined") { e = document.createElementNS(svgNS,"text"); }
    else if (!(e instanceof SVGTextElement)) {alert("text(): expected 'text' for existing elem, but got: "+e.tagName); }	
	
    var xscreen = x*xscale;
	e.setAttribute("x", xscreen);
	var yscreen = Yscreen0 + y*yscale;
	e.setAttribute("y", yscreen);
	e.setAttribute("font-size", size);
	if (vertical) {e.setAttribute("transform", "rotate(-90,"+xscreen+","+yscreen+")");}  // transform="rotate(30 20,40)" See: http://stackoverflow.com/questions/11252753/rotate-x-axis-text-in-d3
	//e.setAttributeNS(null,"stroke", colour);
    e.appendChild(document.createTextNode(text));
    svg.appendChild(e);
	return e;
	}

	
function boxplot(xcenter,width,ystats, elms) {
	// if (boxplot_elems.length=0) {}
	//console.log("*** BOXPLOT STATS LENGTH:",ystats.length);	
	return [
      rect(xcenter,width,ystats, elms[0]),
	  line(xcenter-0.25*width,ystats[ilowerwisker], xcenter+0.25*width,ystats[ilowerwisker], "1px", false, "black", elms[1]), // lower whisker horizontal line
	  line(xcenter,ystats[ilowerwisker], xcenter,ystats[ilowerhinge], "1px", true, "black", elms[2]),  // lower whisker to box dashed line
	  line(xcenter-0.5*width,ystats[imedian], xcenter+0.5*width,ystats[imedian], "3px", false, "black", elms[3]), // median horizontal line
	  line(xcenter,ystats[iupperhinge], xcenter,ystats[iupperwhisker], "1px", true, "black", elms[4]),  // upper whisker to box dashed line
	  line(xcenter-0.25*width,ystats[iupperwhisker], xcenter+0.25*width,ystats[iupperwhisker], "1px", false, "black", elms[5]) // upper whisker horizontal line
	];
	// return elms; // array of elements for each box.
    }


function update_boxplots() {
  // 
  var wt_points=[],mu_points=[];	
  for (var i=1; i<lines.length; i++) { // corectly starts at i=1, as lines[0] is the boxplot dimensions.
    var col = lines[i].split(",");
    if (col[iy]=='NA') {continue;}
	
    // To determine if point is visible, can check the "visibility" attribute of the point:
    // var id = "c"+i.toString();   // 'c' for circle or cell_line
	// var elem = document.getElementById(id);
	// if (elem.getAttribute("visibility")=="hidden") {continue} // otherwise: "visible"

    // Or more directly check if that tissue checkbox is checked:
    var tissue = col[itissue];
	// 	if (tissue=="BONE") {tissue="OSTEOSARCOMA"; col[itissue]=tissue; lines[i]=col.join(',');} // BONE is "OSTEOSARCOMA" in the tissue_colours array.
//	console.log("tissue:", tissue);
	var checkbox = document.getElementById('cb_'+tissue);
//	console.log("checkbox",checkbox);
	if (! checkbox.checked) {continue}

	var isWT = col[imutant]=="0";  // Wildtype rather than mutant.

    if (isWT) {wt_points.push(parseFloat(col[iy]))}
    else {mu_points.push(parseFloat(col[iy]))}
    }	
    // Or can loop through the tissue lists, but need to check if WT or mutant:
	// for (var i=0; i<tissue_lists[tissue].length; i++) {
	//    var elem = tissue_lists[tissue][i];
	//    elem.getAttribute("visibility") == "hidden") {continue} // otherwise: "visible":
	//    }
	// }
//console.log("wt_points.length: ",wt_points.length);
//console.log("mu_points.length: ",mu_points.length);
  var wt_boxstats=boxplot_stats(wt_points);
  var mu_boxstats=boxplot_stats(mu_points);
  
//  console.log(wt_boxstats);
//  console.log(mu_boxstats);
	
  // We have stored the boxplot lines and rectangle in two global array, so can adjust position later:
  boxplot( wtxc, boxwidth, wt_boxstats, wt_boxplot_elems); // don't need "wt_boxplot_elems = ..." as element ids unchanged, just their positions are changed.  
  boxplot( muxc, boxwidth, mu_boxstats, mu_boxplot_elems); // mu_boxplot_elems = 
  
  return true;
  }
	
function showhide_cell_clicked(e) {  // elem can be a 'td' or checkbox.
// When the checkbox is clicked: IE seems to call this checkbox code first then the 'td' click event, whereas Chrome and Firefox seem to call the 'td' event first, then the checkbox event.
    // Not using event as not passed in Firefox when inline onclick="" used
	e = e || window.event;  // Need: window.event for IE <=8
	//e.preventDefault(); // should cancel the also click cell event
//	e.stopPropagation(); // To stop propagation to parent element. ie. stops the event from bubbling up the event chain.
// see: http://stackoverflow.com/questions/5963669/whats-the-difference-between-event-stoppropagation-and-event-preventdefault
//e.cancelBubble  // for IE<=8 
//or maybe use jquery e.stopPropagation...

	var elem = e.target || e.srcElement;
//console.log('showhide_cell: '+elem.id);
    if (elem.id.substring(0,3)=='cb_') {
//	     console.log('leaving showhide_cell');
	    return true; // Need to return true so will be handled by the checkbox click event (showhide_tissue(e)).
	}
	var tissue = elem.id; /// the checkbox name is the tissue.
//	console.log(tissue);
    tissue=tissue.substring(3); // remove the 'td_'
//console.log(tissue);
	//window.event.preventDefault(); // should cancel the also click cell event
   	var checkbox = document.getElementById('cb_'+tissue);
	// checkbox.click();
	checkbox.checked = ! checkbox.checked; // Toggle checked state, but doesn't fire the onchanged event.
	set_tissue_visibility(tissue, checkbox.checked, true)
    // checkbox.dispatchEvent(new Event('change')); // so need to trigger the change event.	
// [1]: Earlier versions of IE instead only support the proprietary EventTarget.fireEvent() method.
    return false;
    }


function set_tissue_visibility(tissue,visible, updateboxplots) {
	for (var i=0; i<tissue_lists[tissue].length; i++) {
	    var elem = tissue_lists[tissue][i];
	    elem.setAttribute("visibility", visible ? "visible":"hidden");
	    }
	if (updateboxplots) {update_boxplots();} // To move the boxplots to match the changes. But if clicked All/None/Toggle buttons then update at end rather than for each tissue.
	}

	
function showhide_tissue(e) {
    // see: http://stackoverflow.com/questions/24578837/remove-or-hide-svg-element

	e = e || window.event;  // Need: window.event for IE <=8
	//e.preventDefault(); // should cancel the also click cell event
//	e.stopPropagation(); // To stop propagation to parent element. ie. stops the event from bubbling up the event chain.
//e.cancelBubble  // for IE<=8 
//or maybe use jquery e.stopPropagation...

//if (!e) e = window.event;
//    e.cancelBubble = true;
//    if (e.stopPropagation) e.stopPropagation();
//}

	var checkbox = e.target || e.srcElement;
//console.log('checkbox '+checkbox.id);
	var tissue = checkbox.id.substring(3); /// the checkbox name is the 'cb_'+tissue.

	set_tissue_visibility(tissue, checkbox.checked, true);
	return false; // does true mean event was handled?
    }
   

function tissue_checkboxes(action) {
	//e = e || window.event;  // Need: window.event for IE <=8
	//var checkbox = e.target || e.srcElement;   
    //var visibility = checkbox.checked ? "visible" : "hidden";
    for (tissue in tissue_lists) {
   	  var checkbox = document.getElementById('cb_'+tissue);

	  switch(action) {
	    case 'all': checkbox.checked = true; break; 
	    case 'none': checkbox.checked = false; break;
  	    case 'toggle': checkbox.checked = ! checkbox.checked; break; // Toggle checked state, but doesn't fire the onchanged event.
		default: alert('Invalid action for tissue_checkboxes(): "'+action+'"');
      }
	  set_tissue_visibility(tissue, checkbox.checked, false); // 'false' as will update boxplot once at end after this loop.
		
      //checkbox.dispatchEvent(new Event('change')); // so need to trigger the change event.
	  
	  // BUT this may not fire the changed event: To make sure the event fires, call the click() method of the checkbox element, like this:  document.getElementById('checkbox').click();
	  
//However, this toggles the checked status of the checkbox, instead of specifically setting it to true or false. Remember that the //change event should only fire, when the checked attribute actually changes.
// It also applies to the jQuery way: setting the attribute using prop or attr, does not fire the change event.
// http://stackoverflow.com/questions/8206565/check-uncheck-checkbox-with-javascript

      }
	update_boxplots();  
    }

	
	
function download_boxplot(download_type, driver, target, histotype, study_pmid) {
   // download_type can be 'png', 'svg', or 'csv'.
   
   // Uses the "svg_todataurl"
   
   //var study_without_brackets = study_pmid.replace('(','').replace(')','');
   //var filename = driver+"_"+target+"_"+histotype+"_"+study_without_brackets+"."+download_type;
   
   var filename = driver+"_"+target+"_"+histotype+"_pmid"+study_pmid+"."+download_type;   
   
   //'In Internet Explorer: with mouse pointer on the boxplot image, click the RIGHT mouse button, then from the popup menu choose "Save picture as...", then in the save dialog that appears, for the "Save as type" choose "PNG (*.png)", the "Save".'
   
   //'If you are using Internet Explorer: with mouse pointer on the boxplot image, click the RIGHT mouse button, then from the popup menu choose "Save picture as...", then in the save dialog that appears, for the "Save as type" choose "PNG (*.png)", then "Save". If that doesn\'t work, then then try Firefox, Opera, Chrome or Safari browsers.'
   
   // This seems to be another way around this issue in IE, and demo shows that the Native toDataURI doesn't work in my IE11 when I tried their demo site: https://github.com/sampumon/SVG.toDataURL
   // but their alternative should work.

   // canvas2image library: https://github.com/hongru/canvas2image
   
   // **** deprecated “svgElement.offsetWidth/height” on Chrome: http://stackoverflow.com/questions/35568259/how-to-replace-the-deprecated-svgelement-offsetwidth-height-on-chrome
/*   
   e.getBoundingClientRect()

   // when there is no scale: or remove any parent transforms first.
   var rect = e.getBoundingClientRect();

  i = 0;
  cur = elm;


  //restore the transform for all ancestors
  while (cur) {
    if (cur.style) {
      cur.style.transform = saveTransforms[i];
    }
    i++;
    cur = cur.parentNode;
  }


  return rect.width;
}
*/


// **** GOOD javascript event handlers and 'this': http://www.sitepoint.com/javascript-this-event-handlers/
// Avoid using inline events:   onclick="return EventHandler(this);">
//  https://github.com/jquery/jquery/issues/2889
// Apparently: This is harmless, undefined < 0 is false so when these properties get removed, this method will automatically start using the getClientRects().length check.
   
   // Downloading a canvas as an image:
   // var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");  // here is the most important part because if you dont replace you will get a DOM 18 exception.
   // window.location.href=image; // it will save locally
   
   
    //var img = document.getElementById("fromcanvas");
   
    // var img = document.createElement('canvas'); // var img = document.getElementById("fromcanvas");
    //canvas.width = image.width; // set by the library
    //canvas.height = image.height;


	
	// saving SVG as Image: http://techslides.com/save-svg-as-an-image
	
	// SVG Crowbar helpfully inlines any stylesheets you may have on the page, but you might find you need to edit a few of the styles by hand to get things to look right. For example, the font-family “sans-serif” won’t work in an SVG image, even though it works when the SVG is built client-side; you’ll have to make the font name explicit, such as “Helvetica” or “Arial”.  From: Other waays maybe: https://bl.ocks.org/mbostock/6466603
	
	// Maybe SVG to svg file using: var dataUrl = 'data:image/svg+xml,'+encodeURIComponent(svgString);
	
	// Pablo has functions for saving PNGs, etc: http://pablojs.com/
	
	// http://stackoverflow.com/questions/3173048/is-there-an-equivalent-of-canvass-todataurl-method-for-svg
	// var SVGtopngDataURL = document.getElementById("svg_element_id").toDataURL("image/png");


	switch (download_type) {
	case 'svg':
	  show_message("download_SVG_boxplot", "Downloading..."); // maybe warn if browser is IE
	  mysvg.toDataURL("image/svg+xml", {		  
	    callback: function(data) {download_data(data,filename)}
      });
	  break;
	    
	  
    case 'png':
	  show_message("download_PNG_boxplot", "Downloading..."); // maybe warn if browser is IE
      var ua = window.navigator.userAgent;  // if ($.browser.msie) {alert($.browser.version);}	
      var ie = ((ua.indexOf('MSIE ') > 0) || (ua.indexOf('Trident/')>0));  // 'MSIE' for IE<=10; 'Trident/' for IE 11; || (ua.indexOf('Edge/')>0) for Edge (IE 12+)
	  var render = ie ? "canvg" : "native";  // Using "canvg" for IE, to avoid the SECURITY_ERR in IE: canvas.toDataURL(type)	
      mysvg.toDataURL("image/png", {
  	    callback: function(data) {
		    download_data(data,filename)
			},
		renderer: render 
      });
	  break;

    // The following might work, but will just request a download from the webserver:
    case 'csv':
	  saveTextAsFile(boxplot_csv,filename,"text/csv")  // or "text/plain" or "text/json"
      // The following doesn't seem to work, so will just request a download from the webserver:
      //  var data = encodeURIComponent('data:text/csv;charset=utf-8,' + boxplot_csv); // was: encodeURI(.....);
	  // For JSON, use: var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));  
      // download_data('CSV file', data, filename);
      break;
  
	default: alert("Invalid download_type: '"+download_type+"'")
	}
	
   // previously used: saveSvgAsPng(svg, png_filename);
   
   // http://weworkweplay.com/play/saving-html5-canvas-as-image/
  }

   
   // Alternative to save as SVG use:
   // http://stackoverflow.com/questions/2483919/how-to-save-svg-canvas-to-local-filesystem

function download_data(data, filename) {
    // This probably doesn't work in IE, and 'download' attribute is only HTML5:
    var a = document.createElement('a');
    a.setAttribute('href', data);
    a.setAttribute('target', '_blank');	// or: 	a.target = '_blank';
    a.setAttribute('download', filename);	
	document.body.appendChild(a);    // as link has to be on the document - needed in Firefox, etc.
	a.click();
    document.body.removeChild(a);
	// http://halistechnology.com/2015/05/28/use-javascript-to-export-your-data-as-csv/
	// http://cwestblog.com/2014/10/21/javascript-creating-a-downloadable-file-in-the-browser/
	// **GOOD: http://hackworthy.blogspot.co.uk/2012/05/savedownload-data-generated-in.html
	// http://stackoverflow.com/questions/4184944/javascript-download-data-to-file-from-content-within-the-page
	// FileSaver Library (supports IE10+) : https://github.com/eligrey/FileSaver.js/
	// http://stackoverflow.com/questions/35148578/download-a-text-file-from-textarea-on-button-click
	// for earlier browsers flash: https://github.com/dcneiner/Downloadify	
    }
	

	
function saveTextAsFile(data,filename,mimetype) {
	// mimetype should be, eg: "text/csv" or "text/plain"
	// Based on: http://stackoverflow.com/questions/35148578/download-a-text-file-from-textarea-on-button-click

    var textFileAsBlob = new Blob([data], { type: mimetype }); // create a new Blob (html5 magic) that conatins the data from your form field
    var a = document.createElement("a");
    a.download = filename;
    a.innerHTML = "My Hidden Link";
    // allow code to work in webkit & Gecko based browsers without the need for a if / else block.
    window.URL = window.URL || window.webkitURL;    
    a.href = window.URL.createObjectURL(textFileAsBlob); // Create the link Object.
    // when link is clicked call a function to remove it from the DOM in case user wants to save a second file.
    a.onclick = destroyClickedElement;
    a.style.display = "none";         // make sure the link is hidden.
    document.body.appendChild(a);  // add the link to the DOM
    a.click();      // click the new link
    }

function destroyClickedElement(event) {
    // remove the link from the DOM
    document.body.removeChild(event.target);
    }




	
function img_and_link() {
// "There is no need to do base64 encoding - you can create a link with raw SVG code in it. Here is a modified function encode_as_img_and_link() from The_Who's answer:"
  $('body').append(
    $('<a>')
      .attr('href-lang', 'image/svg+xml')
      .attr('href', 'data:image/svg+xml;utf8,' +  unescape($('#mysvg').outerHTML))
      .text('Download')
  );
}  
  // Better might be: https://gist.github.com/jweir/706988
// This example was created using Protovis & jQuery
// Base64 provided by http://www.webtoolkit.info/
function encode_as_img_and_link(){
 // Add some critical information
 $("svg").attr({ version: '1.1' , xmlns:"http://www.w3.org/2000/svg"});

 var svg = $("#chart-canvas").html();
 var b64 = Base64.encode(svg);

 // Works in recent Webkit(Chrome)
 $("body").append($("<img src='data:image/svg+xml;base64,\n"+b64+"' alt='file.svg'/>"));

 // Works in Firefox 3.6 and Webit and possibly any browser which supports the data-uri
 $("body").append($("<a href-lang='image/svg+xml' href='data:image/svg+xml;base64,\n"+b64+"' title='file.svg'>Download</a>"));
}

function test_save() {
// or maybe save SVG: http://stackoverflow.com/questions/2483919/how-to-save-svg-canvas-to-local-filesystem
	$('#SVGsave').click(function(){
		var a      = document.createElement('a');
		a.href     = 'data:image/svg+xml;utf8,' + unescape($('#SVG')[0].outerHTML);
		a.download = 'plot.svg';
		a.target   = '_blank';
		document.body.appendChild(a); a.click(); document.body.removeChild(a);
	});  
  
}


/*
// Alternatively sent to server to render:

<button onclick="sendSVG();">Save as SVG File</button>

(3) Include the JavaScript function named in your button markup:

function sendSVG() 
{
   var svgText = document.getElementById('svg').innerHTML;

   var form = document.createElement("form");
   form.setAttribute("method", "post");
   form.setAttribute("action", "http://path-to-your-server-app");
   form.setAttribute("accept-charset", "UTF-8");

   var hiddenSVGField = document.createElement("input");    
   hiddenSVGField.setAttribute("type", "hidden");
   hiddenSVGField.setAttribute("name", "svgText");
   hiddenSVGField.setAttribute("value", svgText);

   form.appendChild(hiddenSVGField);
   document.body.appendChild(form);
   form.submit();
}
(4) Write a server app to accept your SVGtext post request and return as image/svg+xml using Content-Disposition to specify an attachment. Working code in three languages is presented, although I am not a Perl programmer and have never used PHP in anger.

Java Servlet

public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException
{
   String svgText = (String) request.getParameter("svgText");
   response.setContentType("image/svg+xml");
   response.addHeader("Content-Disposition", "attachment; filename=\"image.svg\"");
   PrintWriter out = response.getWriter();
   out.println(svgText);
}
Perl CGI

use CGI qw(:standard);
my $svgText = param('svgText');
print header(-type => "image/svg+xml",
    -content_disposition => "attachment; filename=image.svg");      
print $svgText;
PHP

<?php
   $svgText = $_POST['svgText'];
   header('Content-type: image/svg+xml');
   header('Content-Disposition: attachment; filename="image.svg"'); 
   print "$svgText";
?>
I have used a hard-coded name for the image here (image.svg), but actually pick up a discriptor of the dynamic content I generate from the page (using a div and an ID again, and document.getElementById('graphName').textContent).
*/
  
  
/*  
Why is "MFM223,NA" - NA?  
79,-2,2,-0.69,0.04,0.455,0.78,1.36,-0.95,-0.48,-0.205,0.25,0.63;BONE,143B,0.75,0;BONE,CAL72,0.53,0;BONE,G292,0.04,0;BONE,HOS,-0.04,0;BONE,HUO3N1,-0.27,0;BONE,HUO9,1.18,0;BONE,MG63,0.09,0;BONE,NOS1,0.51,0;BONE,NY,1.36,0;BONE,SAOS2,-0.08,0;BONE,SJSA1,0.02,0;BONE,U2OS,0.03,0;BREAST,BT20,1,0;BREAST,BT549,-0.6,0;BREAST,CAL120,0.86,0;BREAST,CAL51,0.88,0;BREAST,CAMA1,-1.2,0;BREAST,DU4475,0.37,0;BREAST,HCC38,0.14,0;BREAST,HCC70,0.65,0;BREAST,HS578T,0.58,0;BREAST,MCF7,0.96,0;BREAST,MDAMB157,0.07,0;BREAST,MDAMB231,0.93,0;BREAST,MDAMB436,0.58,0;BREAST,MFM223,NA,0;BREAST,T47D,0.89,0;BREAST,BT474,-0.25,1;BREAST,HCC1954,-0.25,1;BREAST,HCC202,-0.71,1;BREAST,JIMT1,-0.95,1;BREAST,MDAMB453,-0.24,1;BREAST,ZR7530,0.1,1;LUNG,A427,-0.47,0;LUNG,A549,0.16,0;LUNG,BEN,1.11,0;LUNG,H1299,0.49,0;LUNG,H1650,0.4,0;LUNG,H1838,0.54,0;LUNG,H1975,1.03,0;LUNG,H2228,0.77,0;LUNG,H23,0.29,0;LUNG,H2342,0.7,0;LUNG,H292,0.52,0;LUNG,H358,0.11,0;LUNG,H460,-0.23,0;LUNG,H727,0.93,0;HEADNECK,PCI30,-0.23,0;PANCREAS,ASPC1,0.79,0;PANCREAS,BXPC3,0.32,0;PANCREAS,MIAPACA2,0.78,0;CERVICAL,C33A,-0.65,0;CERVICAL,CASKI,0.86,0;CERVICAL,HELA,-0.03,0;CERVICAL,SIHA,0.43,0;OVARY,CAOV3,0.18,0;OVARY,ES2,0.53,0;OVARY,OAW42,0.2,0;OVARY,OV90,1.2,0;OVARY,OVISE,0.26,0;OVARY,OVMANA,0.49,0;OVARY,OVTOKO,0.05,0;OVARY,TOV112D,0.69,0;OVARY,TOV21G,0.3,0;OVARY,RMGI,-0.73,1;OVARY,SKOV3,0.55,1;OESOPHAGUS,FLO1,-0.69,0;OESOPHAGUS,SKGT4,-0.03,0;OESOPHAGUS,TE1,0.53,0;OESOPHAGUS,TE10,0.96,0;OESOPHAGUS,TE11,0.44,0;OESOPHAGUS,TE8,1.1,0;OESOPHAGUS,TE9,-0.11,0;OESOPHAGUS,ESO26,0.34,1;OESOPHAGUS,OE19,-0.17,1;OESOPHAGUS,OE33,0.63,1;OESOPHAGUS,TE6,0.16,1;ENDOMETRIUM,MFE296,0.47,0;CENTRAL_NERVOUS_SYSTEM,KNS42,-0.31,0

79,-2,2,-0.69,0.04,0.455,0.78,1.36,-0.95,-0.48,-0.205,0.25,0.63;BONE,143B,0.75,0;,CAL72,0.53,0;,G292,0.04,0;,HOS,-0.04,0;,HUO3N1,-0.27,0;,HUO9,1.18,0;,MG63,0.09,0;,NOS1,0.51,0;,NY,1.36,0;,SAOS2,-0.08,0;,SJSA1,0.02,0;,U2OS,0.03,0;BREAST,BT20,1,0;,BT549,-0.6,0;,CAL120,0.86,0;,CAL51,0.88,0;,CAMA1,-1.2,0;,DU4475,0.37,0;,HCC38,0.14,0;,HCC70,0.65,0;,HS578T,0.58,0;,MCF7,0.96,0;,MDAMB157,0.07,0;,MDAMB231,0.93,0;,MDAMB436,0.58,0;,MFM223,NA,0;,T47D,0.89,0;,BT474,-0.25,1;,HCC1954,-0.25,1;,HCC202,-0.71,1;,JIMT1,-0.95,1;,MDAMB453,-0.24,1;,ZR7530,0.1,1;LUNG,A427,-0.47,0;,A549,0.16,0;,BEN,1.11,0;,H1299,0.49,0;,H1650,0.4,0;,H1838,0.54,0;,H1975,1.03,0;,H2228,0.77,0;,H23,0.29,0;,H2342,0.7,0;,H292,0.52,0;,H358,0.11,0;,H460,-0.23,0;,H727,0.93,0;HEADNECK,PCI30,-0.23,0;PANCREAS,ASPC1,0.79,0;,BXPC3,0.32,0;,MIAPACA2,0.78,0;CERVICAL,C33A,-0.65,0;,CASKI,0.86,0;,HELA,-0.03,0;,SIHA,0.43,0;OVARY,CAOV3,0.18,0;,ES2,0.53,0;,OAW42,0.2,0;,OV90,1.2,0;,OVISE,0.26,0;,OVMANA,0.49,0;,OVTOKO,0.05,0;,TOV112D,0.69,0;,TOV21G,0.3,0;,RMGI,-0.73,1;,SKOV3,0.55,1;OESOPHAGUS,FLO1,-0.69,0;,SKGT4,-0.03,0;,TE1,0.53,0;,TE10,0.96,0;,TE11,0.44,0;,TE8,1.1,0;,TE9,-0.11,0;,ESO26,0.34,1;,OE19,-0.17,1;,OE33,0.63,1;,TE6,0.16,1;ENDOMETRIUM,MFE296,0.47,0;CENTRAL_NERVOUS_SYSTEM,KNS42,-0.31,0


ERBB2_2064_ENSG00000141736      DGKG_ENSG00000058866    12      66      0.0022609665152334      0.759469696969697       -0.205  0.455   -0.66   79,-2,2,-0.69,0.04,0.455,0.78,1.36,-0.95,-0.48,-0.205,0.25,0.63;BONE,143B,0.75,0;BONE,CAL72,0.53,0;BONE,G292,0.04,0;BONE,HOS,-0.04,0;BONE,HUO3N1,-0.27,0;BONE,HUO9,1.18,0;BONE,MG63,0.09,0;BONE,NOS1,0.51,0;BONE,NY,1.36,0;BONE,SAOS2,-0.08,0;BONE,SJSA1,0.02,0;BONE,U2OS,0.03,0;BREAST,BT20,1,0;BREAST,BT549,-0.6,0;BREAST,CAL120,0.86,0;BREAST,CAL51,0.88,0;BREAST,CAMA1,-1.2,0;BREAST,DU4475,0.37,0;BREAST,HCC38,0.14,0;BREAST,HCC70,0.65,0;BREAST,HS578T,0.58,0;BREAST,MCF7,0.96,0;BREAST,MDAMB157,0.07,0;BREAST,MDAMB231,0.93,0;BREAST,MDAMB436,0.58,0;BREAST,MFM223,NA,0;BREAST,T47D,0.89,0;BREAST,BT474,-0.25,1;BREAST,HCC1954,-0.25,1;BREAST,HCC202,-0.71,1;BREAST,JIMT1,-0.95,1;BREAST,MDAMB453,-0.24,1;BREAST,ZR7530,0.1,1;LUNG,A427,-0.47,0;LUNG,A549,0.16,0;LUNG,BEN,1.11,0;LUNG,H1299,0.49,0;LUNG,H1650,0.4,0;LUNG,H1838,0.54,0;LUNG,H1975,1.03,0;LUNG,H2228,0.77,0;LUNG,H23,0.29,0;LUNG,H2342,0.7,0;LUNG,H292,0.52,0;LUNG,H358,0.11,0;LUNG,H460,-0.23,0;LUNG,H727,0.93,0;HEADNECK,PCI30,-0.23,0;PANCREAS,ASPC1,0.79,0;PANCREAS,BXPC3,0.32,0;PANCREAS,MIAPACA2,0.78,0;CERVICAL,C33A,-0.65,0;CERVICAL,CASKI,0.86,0;CERVICAL,HELA,-0.03,0;CERVICAL,SIHA,0.43,0;OVARY,CAOV3,0.18,0;OVARY,ES2,0.53,0;OVARY,OAW42,0.2,0;OVARY,OV90,1.2,0;OVARY,OVISE,0.26,0;OVARY,OVMANA,0.49,0;OVARY,OVTOKO,0.05,0;OVARY,TOV112D,0.69,0;OVARY,TOV21G,0.3,0;OVARY,RMGI,-0.73,1;OVARY,SKOV3,0.55,1;OESOPHAGUS,FLO1,-0.69,0;OESOPHAGUS,SKGT4,-0.03,0;OESOPHAGUS,TE1,0.53,0;OESOPHAGUS,TE10,0.96,0;OESOPHAGUS,TE11,0.44,0;OESOPHAGUS,TE8,1.1,0;OESOPHAGUS,TE9,-0.11,0;OESOPHAGUS,ESO26,0.34,1;OESOPHAGUS,OE19,-0.17,1;OESOPHAGUS,OE33,0.63,1;OESOPHAGUS,TE6,0.16,1;ENDOMETRIUM,MFE296,0.47,0;CENTRAL_NERVOUS_SYSTEM,KNS42,-0.31,0

ERBB2_2064_ENSG00000141736      DGKG_ENSG00000058866    12      67      0.0022609665152334      0.763059701492537       range,-2,2;wt_box,-0.69,0.04,0.455,0.78,1.36;mu_box,-0.95,-0.48,-0.205,0.25,0.63;BONE,143B,1.27,0.75,0;BONE,CAL72,1.28,0.53,0;BONE,G292,0.82,0.04,0;BONE,HOS,1.11,-0.04,0;BONE,HUO3N1,0.99,-0.27,0;BONE,HUO9,1.23,1.18,0;BONE,MG63,1.09,0.09,0;BONE,NOS1,1.17,0.51,0;BONE,NY,0.78,1.36,0;BONE,SAOS2,0.74,-0.08,0;BONE,SJSA1,1.31,0.02,0;BONE,U2OS,1.26,0.03,0;BREAST,BT20,1.07,1,0;BREAST,BT549,1.24,-0.6,0;BREAST,CAL120,0.72,0.86,0;BREAST,CAL51,0.9,0.88,0;BREAST,CAMA1,1.08,-1.2,0;BREAST,DU4475,1.32,0.37,0;BREAST,HCC38,1.04,0.14,0;BREAST,HCC70,0.95,0.65,0;BREAST,HS578T,1.11,0.58,0;BREAST,MCF7,1.21,0.96,0;BREAST,MDAMB157,1.03,0.07,0;BREAST,MDAMB231,1.26,0.93,0;BREAST,MDAMB436,0.93,0.58,0;BREAST,MFM223,0.78,NA,0;BREAST,T47D,0.9,0.89,0;BREAST,BT474,1.82,-0.25,1;BREAST,HCC1954,1.82,-0.25,1;BREAST,HCC202,1.97,-0.71,1;BREAST,JIMT1,2.09,-0.95,1;BREAST,MDAMB453,1.77,-0.24,1;BREAST,ZR7530,1.77,0.1,1;LUNG,A427,1.3,-0.47,0;LUNG,A549,0.96,0.16,0;LUNG,BEN,0.91,1.11,0;LUNG,H1299,1.3,0.49,0;LUNG,H1650,0.7,0.4,0;LUNG,H1838,0.73,0.54,0;LUNG,H1975,1.27,1.03,0;LUNG,H2228,1.17,0.77,0;LUNG,H23,1.17,0.29,0;LUNG,H2342,1.23,0.7,0;LUNG,H292,1,0.52,0;LUNG,H358,1.1,0.11,0;LUNG,H460,1.24,-0.23,0;LUNG,H727,1.25,0.93,0;HEADNECK,PCI30,1.12,-0.23,0;PANCREAS,ASPC1,1.2,0.79,0;PANCREAS,BXPC3,0.71,0.32,0;PANCREAS,MIAPACA2,1.12,0.78,0;CERVICAL,C33A,0.89,-0.65,0;CERVICAL,CASKI,1.18,0.86,0;CERVICAL,HELA,1.02,-0.03,0;CERVICAL,SIHA,0.83,0.43,0;OVARY,CAOV3,1.06,0.18,0;OVARY,ES2,1.22,0.53,0;OVARY,OAW42,1.33,0.2,0;OVARY,OV90,1.2,1.2,0;OVARY,OVISE,0.88,0.26,0;OVARY,OVMANA,0.71,0.49,0;OVARY,OVTOKO,1.08,0.05,0;OVARY,TOV112D,1.06,0.69,0;OVARY,TOV21G,1.16,0.3,0;OVARY,RMGI,1.92,-0.73,1;OVARY,SKOV3,2.07,0.55,1;OESOPHAGUS,FLO1,1.15,-0.69,0;OESOPHAGUS,SKGT4,1.16,-0.03,0;OESOPHAGUS,TE1,0.9,0.53,0;OESOPHAGUS,TE10,1.09,0.96,0;OESOPHAGUS,TE11,1.23,0.44,0;OESOPHAGUS,TE8,0.81,1.1,0;OESOPHAGUS,TE9,0.98,-0.11,0;OESOPHAGUS,ESO26,1.88,0.34,1;OESOPHAGUS,OE19,1.73,-0.17,1;OESOPHAGUS,OE33,1.89,0.63,1;OESOPHAGUS,TE6,1.71,0.16,1;ENDOMETRIUM,MFE296,0.84,0.47,0;CENTRAL_NERVOUS_SYSTEM,KNS42,1.24,-0.31,0;count,79
*/
  
function fetch_data(driver,target,histotype,study_pmid) {
    // var url = global_url_gene_info_for_mygene.replace('mygene',gene_name);
    //driver="ERBB2";
	//target="CASK";
	//target="DGKG"; // ERBB3, FASTK
	//tissue="PANCAN";
	//study="26947069";
	
	boxplot_csv=''; // or undefined ? // is global to indicate that no data has been retrieved yet.
		
	//var url = "http://localhost:8000/gendep/get_boxplot_csv/"+driver+"/"+target+"/"+histotype+"/"+study_pmid+"/";
		
	var url = global_url_for_boxplot_data.replace('myformat','csvplot').replace('mydriver',driver).replace('mytarget',target).replace('myhistotype',histotype).replace('mystudy',study_pmid);
    
    $.ajax({
        url: url,
        dataType: 'text',  // use 'text' as there is no specific 'csv' option for this.
        })
        .done(function(data, textStatus, jqXHR) {  // or use .always(...)
//console.log(data);
//		alert(data);
			boxplot_csv=data;
			draw_svg_boxplot(driver, target);
			
//            if (data['success']) {
//
//				}
//			  else {callback("Error: "+data['message'])}
		})
		.fail(function(jqXHR, textStatus, errorThrown) {
		    alert("Ajax Failed: '"+textStatus+"'  '"+errorThrown+"'");
        });
	return true; // To the fancybox afterLoad, so that the fancy box content is shown.		
    }


  /* NOTES:
 <!-- the tag: version="1.1" is not used by any browsers -->
 
	   r: 10;  
	As "r" is not a style, an alternative way is to make the stroke-width bigger on hoover. http://stackoverflow.com/questions/14255631/style-svg-circle-with-css 
  */
  
  /* stroke: black; */
      /* stroke-width: 1px; */
	/* shape-rendering: crispEdges; Not needed if placed at half pixel	*/
/*circle:
		   r: 5; */
	/* As "r" is not a style, an alternative way is to make the stroke-width bigger on hoover. http://stackoverflow.com/questions/14255631/style-svg-circle-with-css 

	stroke-width:10px;	

  <!--circle id="my-circle" cx="100" cy="100" r="50" /-->
  <!-- polyline points="20,20 380,20 380,380 20,380 20,20" style="fill:none;stroke:black;stroke-width:2" /-->
  <!-- rect x="50" y="10" width="349" height="340" stroke="yellow" fill="none" stroke-width="2" /-->
*/  
		   


function show_svg_boxplot_in_fancybox(driver, target, histotype, study_pmid, wilcox_p, effect_size, zdelta_score, target_info, target_variant) {

  // Only draw the svg after fancybox content has loaded as needs "mysvg" tag), and AJAX has retrned the data.
  svg_fancybox_loaded = false;
  drawing_svg = false;
  boxplot_csv = '';
  fetch_data(driver,target,histotype,study_pmid);	  // is asynchronous AJAX call.

  var comma = "','";
  var parameters = "'"+driver +comma+ target +comma+ histotype +comma+ study_pmid+"'";
  //console.log(parameters);
  
  var download_boxplot_csv_url = global_url_for_boxplot_data.replace('myformat','download').replace('mydriver',driver).replace('mytarget',target).replace('myhistotype',histotype).replace('mystudy',study_pmid);  

  var download_csv_click = 'show_message(\'download_CSV_boxplot\', \'Downloading...\');'
  
//  $("#download_boxplot_csv_form")
//      .attr("action", download_boxplot_csv_url)
//      .submit(function( event ) {
//         show_message("download_message", "Downloading CSV file ....."); // maybe warn if browser is IE       
	     //return true;
//       });
// The background colour of the downloaded PNG file is transparent. To get a white background as requested, can try: http://stackoverflow.com/questions/11293026/default-background-color-of-svg-root-element  
// <svg style='stroke-width: 0px; background-color: blue;'> </svg>  
// but This causes all sub-element strokes to be zero-width as well, so its not a good "background" option. –
// SVG version 1.2 has viewport-fill I'm not sure how widely implemented this property is though as most browsers are targetting SVG 1.1 at this time. Opera implements it FWIW. A more cross-browser solution currently would be to stick a <rect> element with width and height of 100% and fill="red" as the first child of the <svg> element
// if want a box around the plot, to the "rect" can add: stroke-width:0;stroke:black;stroke-opacity:1.0

// if change the sv dimensions, remember to also change the background rect dimensions:
  var mycontent = '<table align="center" style="padding:0; border-collapse: collapse; border-spacing: 0;">'
  + '<tr><td style="padding:0;">'
  + '<svg id="mysvg" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'+svgWidth.toString()+'" height="'+svgHeight.toString()+'">'
  + '<style>'
  + ' line{stroke-opacity: 1.0;}'
  + ' rect{fill: none; stroke: black; stroke-width: 1px; stroke-opacity: 1.0;}'
  + ' circle {fill-opacity: 0.9; stroke-width: 1px; stroke: black;}'
  + ' circle:hover {opacity: 0.9; stroke: black;}'
  + ' text {font-family: sans-serif; word-spacing: 2; text-anchor: middle;}'
  + '</style>'
  + '<rect x="0" y="0" width="'+svgWidth.toString()+'" height="'+svgHeight.toString()+'" style="fill:white;stroke-width:0;fill-opacity:1.0;"/>'
  + 'Sorry, your browser does not support inline SVG.'
  + '</svg>'
  + '</td><td style="vertical-align:middle; padding:0;">'
  + '<table id="legend_table" class="tablesorter"></table>'
  + '<table style="padding:0; border-collapse: collapse; border-spacing: 0;"><tr><td style="font-size:80%">Download boxplot as:'
  + '</td><td><input type="button" id="download_PNG_boxplot" value="PNG image" data-value="PNG image" onclick="download_boxplot(\'png\','+parameters+');"/> '
  + '</td><td><form id="download_boxplot_form" method="get" action="'+download_boxplot_csv_url+'">'   
  + '<input type="submit" id="download_CSV_boxplot" value="CSV file" data-value="CSV file" onclick="'+download_csv_click+'"/>'  
  + '</form></td></tr></table>'  
  + '<table style="padding:0; border-collapse: collapse; border-spacing: 0;"><tr><td style="font-size:80%">Download legend for:'  
  + '</td><td><input type="button" id="download_selected_legend" value="Selected tissues" data-value="Selected tissues" onclick="download_legend(\'selected\');"/> '
  + '</td><td><input type="button" id="download_all_legend" value="All tissues" data-value="All tissues" onclick="download_legend(\'all\');"/> '
  + '</td></tr></table>'
  
  + '<br/><span id="download_message" style="font-size: 70%;"></span>'
  + '</td></tr></table>';
  
  // For testing  drawing the legend:  + '<canvas id="mycanvas">Canvas not supported</canvas>';

  // The download_all_legend was previously a submit button inside a form, so would download a legend from the server, but now generating the legend in the javascript function:
  // <form id="download_legend_form" method="get" action="">
  // <input type="submit" id="download_all_legend" value="All tissues" data-value="All tissues" onclick="download_legend(\'all\');"/>
  // </form>
  
// The SVG download does work, but SVG isn't that useful in practice:
//  + '</td><td><input type="button" id="download_SVG_boxplot" value="SVG image" data-value="SVG image" onclick="download_boxplot(\'svg\','+parameters+');"/> '


// alt="Loading boxplot image...."/

  var study = study_info(study_pmid);

  var plot_title = '<hr/><p id="plot_title" style="margin-top: 0; text-align: center; line-height: 1.7">'
    + '<b><span data-gene="'+driver+'">'+driver+'</span></b>'
	+ ' altered cell lines have an increased dependency upon'
	+ ' <b><span data-gene="'+target+'">'+target+'</span></b></br>'
	+ ' (p='+wilcox_p.replace('e', ' x 10<sup>')+'</sup>'
    + ' | effect size='+effect_size+'%'
    + ' | &Delta;Score='+zdelta_score
	+ ' | Tissues='+ histotype_display(histotype)
	+ ' | Source='+ study[ishortname]
	+ ')</p>';

  var plot_links='';
  if (typeof target_info === 'undefined') {plot_links = 'Unable to retrieve synonyms and external links for this gene';}
  else {
      if (target !== target_info['gene_name']) {alert("Target name:"+target+" != target_info['gene_name']:"+target_info['gene_name'] );}
	  var target_full_name  = '<i>'+target_info['full_name']+'</i>';
	  var target_synonyms   = target_info['synonyms'];
	  if (target_synonyms !== '') {target_synonyms = ' | '+target_synonyms;}
	  
	  var ncbi_summary = target_info['ncbi_summary'];
	  if ((typeof ncbi_summary !=="undefined") && (ncbi_summary!=="")) {ncbi_summary='<p style="font-size:90%; margin-top:0; margin-bottom:0;"><b>Entrez Summary for '+target+':</b> '+ncbi_summary+'</p>'}
	  var target_external_links = gene_external_links(target_info['ids'], '|', false); // returns html for links to entrez, etc. The 'false' means returns the most useful selected links, not all links.
	  
	  plot_links = '<b>'+target+'</b>'+target_synonyms+', '+target_full_name +'<br/>'+target+' Links: '+target_external_links + ncbi_summary;
	  }
// For the following, maybe better just keep left aligned instead as refers to target gene. 	  
  plot_title += '<p style="margin-bottom: 0; text-align: center; line-height: 1.5;">'+plot_links+'</p>';

//===========================================================================
/*
// From the original png boxplot function:
  var mycontent = '.....<tr>
  
  <td ><img src="' + url_boxplot + '" width="'+boxplot_width+'" height"'+boxplot_height+'" alt="Loading boxplot image...."/></td>' + '<td style="padding:0;"><img src="' + url_legend + '" width="'+legend_width+'" height"'+legend_height+'"/></td></tr></table>';
 // console.log(mycontent);
  var study = study_info(study_pmid);
console.log(mycontent);
//console.log(gene_info_cache[target]);
//console.log(target_ids);
    
  
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
   

*/
//============================================================================


/* <input type="button" value="Fetch data" onclick="fetch_data();"> \
<a id="data" href="data:"></a> \
<center><img id="fromcanvas" alt="PNG image will appear below a couple of seconds after the \'PNG image\' button clicked"/></center>
*/
  

/*
A POSSIBLY FASTER ALTERNATIVE TO USING FANCY BOX IS:
  https://docs.djangoproject.com/en/1.9/ref/request-response/#jsonresponse-objects
return JsonResponse(response_data, status=201)
safe=True,
=======  
   // From: http://www.w3schools.com/jsref/met_win_open.asp
   var myWindow = window.open("", "MsgWindow", "width=200,height=100");
   // additional options, eg: toolbar=yes,scrollbars=yes,resizable=yes,top=500,left=500,
   myWindow.document.write("<p>This is 'MsgWindow'. I am 200px wide and 100px tall!</p>");
    // To close window, use:  myWindow.close();   // Closes the new window
  focus() 	Sets focus to the current window
  egt: 
  function popitup(url) {
	newwindow=window.open(url,'name','height=200,width=150');
	if (window.focus) {newwindow.focus()} // tests first if browser supports the focus() method
	return false; // prevents browser following the link
   // Save SVG as image: http://techslides.com/save-svg-as-an-image
   <body onunload="javascript: exitpop()" >
   
   function openWindow(url) {
var width = 500;
var height = 500;
var left = (screen.width - width)/2;
var top = (screen.height - height)/2;
var params = 'width='+ width +', height='+ height+', top='+ top +', left='+ left+ ', resizable=1';
newwin = window.open(url,"Grassmarkers.Com", params);
if (window.focus) {newwin.focus()}
return false;
}
*/

// Count add next/previous buttons: http://jsfiddle.net/xW5gs/
  
  
  // Fancybox options: http://fancyapps.com/fancybox/
// Can use template option to format the close button:  
//  tpl : {
// closeBtn : '<a title="Close" class="fancybox-item fancybox-close" href="javascript:;"></a>'
// }

  $.fancybox.open({
    // href: url_boxplot,
    preload: 0, // Number of gallary images to preload
    //minWidth: 900,
    //mHeight: 750,
	width: 900,
	height: 510,
	minWidth: 900,
	minHeight: 510,
	//width: '100%',
	//height: '100%',
	autoSize: false, // true, //false,  // true,  // false, // otherwise it resizes too tall.
    //padding: 2,  	// is space between image and fancybox, default 15
    //margin:  2, 	// is space between fancybox and viewport, default 20
	// width:  boxplot_width+legend_width+8, // default is 800
	// height: boxplot_height + 8, // default is 600 /// the title is below this again, ie. outside this, so the 25 is just to allow for the margins top and bottom 
    aspectRatio: true,
    //fitToView: true,
	autoCenter: true,
    arrows: false,
	closeEffect : 'none',
    helpers: {
        title: {
            type: 'inside'
        },
        overlay: {
            showEarly: true  // false  // Show as otherwise incorrectly sized box displays before images have arrived.
        }
    },
    // href="{#% static 'gendep/boxplots/' %#}{{ dependency.boxplot_filename }}" 
    // or $(...).content - Overrides content to be displayed - maybe for inline content
	type: 'inline', // 'html', // 'iframe', // 'html',
    //content:
    // href: href,	
	content: mycontent,
	title: plot_title,
	afterLoad: function() {  // Otherwise might draw before ready 
	  svg_fancybox_loaded = true;
	  draw_svg_boxplot();
	}
	
   });
   
   return false; // Return false to the caller so won't move on the page
}	




/*
It seems like if I add an arbitrary delay before trying to drawImage I meet with more success. It seems like 'onload' is firing early on SVG images, before it is actually ready, so when you go to draw the image it fails.


// https://github.com/sampumon/SVG.toDataURL

// Javascript SVG parser and renderer on Canvas
// http://code.google.com/p/canvg/


// detect IE
// returns version of IE or false, if browser is not Internet Explorer
function detectIE() {
    var ua = window.navigator.userAgent;

    var msie = ua.indexOf('MSIE ');
    if (msie > 0) {
        // IE 10 or older => return version number
        return parseInt(ua.substring(msie + 5, ua.indexOf('.', msie)), 10);
    }

    var trident = ua.indexOf('Trident/');
    if (trident > 0) {
        // IE 11 => return version number
        var rv = ua.indexOf('rv:');
        return parseInt(ua.substring(rv + 3, ua.indexOf('.', rv)), 10);
    }

    var edge = ua.indexOf('Edge/');
    if (edge > 0) {
       // Edge (IE 12+) => return version number
       return parseInt(ua.substring(edge + 5, ua.indexOf('.', edge)), 10);
    }

    // other browser
    return false;
}
Sample usage:

alert('IE ' + detectIE());
Default string of IE 10:

Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)
Default string of IE 11:

Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko 
Default string of IE 12 (aka Edge):

Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36 Edge/12.0 
Default string of Edge 13 (thx @DrCord):

Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36 Edge/13.10586


// SVG Java rasteriser (on server): http://xmlgraphics.apache.org/batik/tools/rasterizer.html
*/





