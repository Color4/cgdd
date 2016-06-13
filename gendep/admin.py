from django.contrib import admin
from .models import Study, Gene, Dependency

""" Classes for formatting of the Dejango Admin pages """ 

class StudyAdmin(admin.ModelAdmin):
    list_display  = ('pmid', 'title', 'authors', 'journal', 'pub_date')
    search_fields = ['pmid', 'title', 'authors', 'journal', 'pub_date']


class GeneAdmin(admin.ModelAdmin):
    list_display  = ('gene_name', 'entrez_id', 'ensembl_id', 'full_name')
    search_fields = ['gene_name', 'entrez_id', 'ensembl_id']


class DependencyAdmin(admin.ModelAdmin):
    # For the foreign keys, to return a string need to append: '__gene_name' or use '_id' suffix
    list_display  = ('driver', 'target', 'histotype', 'wilcox_p', 'study')
    search_fields = ['driver_id', 'target_id', 'histotype']
    # search_fields = ['driver__gene_name', 'target__gene_name', 'histotype__full_name']


class CommentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'comment', 'ip', 'date') # optionally add: 'interest'
    search_fields = ['name', 'email', 'comment', 'ip', 'date'] # optionally add: 'interest'

    
admin.site.register(Study, StudyAdmin)
admin.site.register(Gene, GeneAdmin)
admin.site.register(Dependency, DependencyAdmin)
admin.site.register(Comment, CommentAdmin)
