from django.contrib import admin

from .models import Study, Gene, Dependency


class StudyAdmin(admin.ModelAdmin):
    list_display  = ('pmid', 'title', 'authors', 'journal', 'pub_date')
    search_fields = ['pmid', 'title', 'authors', 'journal', 'pub_date']


class GeneAdmin(admin.ModelAdmin):
    list_display  = ('gene_name', 'entrez_id', 'ensembl_id', 'full_name')
    search_fields = ['gene_name', 'entrez_id', 'ensembl_id']


# For the foreign keys, to return a string need to append: '__gene_name'
class DependencyAdmin(admin.ModelAdmin):
    list_display  = ('driver', 'target', 'histotype', 'wilcox_p', 'study_pmid')
    search_fields = ['driver__gene_name', 'target__gene_name', 'histotype']


admin.site.register(Study, StudyAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Dependency, DependencyAdmin)

