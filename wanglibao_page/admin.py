from django.contrib import admin
from django import forms

from ckeditor.widgets import CKEditorWidget
from wanglibao_page.models import Page
from wanglibao_page.models import Catalog
# Register your models here.


class PageAdminForm(forms.ModelForm):
    content =forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Page


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm


class CatalogAdmin(admin.ModelAdmin):
    pass


admin.site.register(Page, PageAdmin)
admin.site.register(Catalog, CatalogAdmin)
