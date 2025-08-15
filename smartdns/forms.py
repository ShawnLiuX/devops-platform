from django import forms
from django.forms import ModelForm, Textarea
from smartdns.models import Cluster, Server, View, Zone, Record


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = ['cname', 'cremark']


class ServerForm(ModelForm):
    class Meta:
        model = Server
        fields = ['sname', 'cluster', 'ip', 'sremark']


class ViewForm(ModelForm):
    class Meta:
        model = View
        fields = ['vname', 'acl', 'vremark']
        widgets = {
            'acl': Textarea(attrs={'cols': 40, 'rows': 10}),
        }


class ZoneForm(ModelForm):
    class Meta:
        model = Zone
        fields = ['zname', 'view', 'zremark']


class RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ['rname', 'rdtype', 'rdata', 'ttl', 'view', 'zone']


class Edit_RecordForm(ModelForm):
    class Meta:
        model = Record
        fields = ['rname', 'rdtype', 'rdata', 'ttl']


class RecordNoteForm(ModelForm):
    class Meta:
        model = Record
        fields = ['rremark']


class RcdUploadFileForm(forms.Form):
    file = forms.FileField(label='记录xls文件')

