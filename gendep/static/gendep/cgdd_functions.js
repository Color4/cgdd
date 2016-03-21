


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
