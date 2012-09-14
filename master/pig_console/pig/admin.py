from django.contrib import admin
from pig.models import PigScript, Jobs


class PigScriptAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'creater', 'date_created',
                    'is_temporery', 'pig_script', )


class JobsAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', )

admin.site.register(PigScript, PigScriptAdmin)
admin.site.register(Jobs, JobsAdmin)
