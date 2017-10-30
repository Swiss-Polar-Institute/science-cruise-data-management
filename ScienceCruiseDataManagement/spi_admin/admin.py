from django.contrib import admin
import spi_admin.models


# Register your models here.

class MailingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    ordering = ['name']


admin.site.register(spi_admin.models.MailingList, MailingListAdmin)
