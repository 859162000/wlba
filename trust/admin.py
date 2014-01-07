from django.db import models
from django.contrib import admin
from django.forms import Textarea
from trust.models import Trust, Issuer

class TrustAdmin (admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs= {'rows':3, 'cols':40})
        }
    }
# Register your models here.
admin.site.register(Trust)
admin.site.register(Issuer)