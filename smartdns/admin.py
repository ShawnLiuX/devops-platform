from django.contrib import admin
from smartdns.models import Server, Zone, View, Record, Audit

class ServerAdmin(admin.ModelAdmin):
    list_display = ('sname', 'ip', 'sremark')

class ViewAdmin(admin.ModelAdmin):
    list_display = ('vname', 'acl', 'vremark')

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('zname', 'view_list', 'zremark')

class RecordAdmin(admin.ModelAdmin):
    list_display = ('rname', 'rdtype', 'rdata', 'ttl', 'rremark', 'view', 'zone')

class AuditAdmin(admin.ModelAdmin):
    list_display = ('id', 'details', 'user', 'add_date')

admin.site.register(Server, ServerAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Audit, AuditAdmin)
