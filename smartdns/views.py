from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django .http import HttpResponseRedirect
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from collections import defaultdict
from smartdns.forms import ClusterForm, ServerForm, ViewForm, ZoneForm, RecordForm, RecordNoteForm, RcdUploadFileForm, Edit_RecordForm
from smartdns.models import Cluster, Server, Zone, View, Record, Audit
import hmac, random
import dns.tsigkeyring
import dns.update
import dns.query
import io
import xlwt
import xlrd


@login_required
def cluster(request):
    if request.method == 'GET':
        results = Cluster.objects.all()
        return render(request, 'smartdns/cluster.html', {'results': results})


@login_required
def cluster_add(request):
    if request.method == 'POST':
        form = ClusterForm(request.POST)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            audit = Audit(user=request.user.username, details='Add Cluster: '+cd['cname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('cluster'))
    else:
        item_en = 'Add Cluster'
        item_ch = '增加集群'
        form = ClusterForm()
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def cluster_del(request, cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)
    if request.method == 'POST':
        href = ''
        message = 'init'

        if Server.objects.filter(cluster=cluster_id):
            message = 'The cluster have server !'
            return render(request, 'confirm.html', {'message': message, 'href': href})

        cluster.delete()
        audit = Audit(user=request.user.username, details='Delete Cluster: '+cluster.cname)
        audit.save()
        return HttpResponseRedirect(reverse('cluster'))
    else:
        item_en = 'Delete Cluster'
        item_ch = '删除集群'
        form = ClusterForm(instance=cluster)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_en})


@login_required
def cluster_mod(request, cluster_id):
    cluster = Cluster.objects.get(id=cluster_id)
    if request.method == 'POST':
        form = ClusterForm(request.POST, instance=cluster)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            audit = Audit(user=request.user.username, details='Edit Cluster: '+cd['cname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('cluster'))
    else:
        item_en = 'Edit Cluster'
        item_ch = '修改集群'
        form = ClusterForm(instance=cluster)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def server(request):
    if request.method == 'GET':
        results = Server.objects.all()
        return render(request, 'smartdns/server.html', {'results': results})


@login_required
def add_server(request):
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            audit = Audit(user=request.user.username, details='Add Server: '+cd['sname']+' '+cd['ip'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('server'))
    else:
        item_en = 'Add Server'
        item_ch = '增加服务器'
        form = ServerForm()
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def delete_server(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.method == 'POST':
        server.delete()
        audit = Audit(user=request.user.username, details='Delete Server: '+server.sname+' '+server.ip)
        audit.save()
        return HttpResponseRedirect(reverse('server'))
    else:
        item_en = 'Delete Server'
        item_ch = '删除服务器'
        form = ServerForm(instance=server)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_en})


@login_required
def edit_server(request, server_id):
    server = Server.objects.get(id=server_id)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            audit = Audit(user=request.user.username, details='Edit Server: '+cd['sname']+' '+cd['ip'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('server'))
    else:
        item_en = 'Edit Server'
        item_ch = '修改服务器'
        form = ServerForm(instance=server)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def view(request):
    if request.method == 'GET':
        results = View.objects.all()
        return render(request, 'smartdns/view.html', {'results': results})


@login_required
def view_key(request, view_id):
    if request.method == 'GET':
        result = View.objects.get(id=view_id)
        return render(request, 'smartdns/view_key.html', {'result': result})


@login_required
def add_view(request):
    if request.method == 'POST':
        form = ViewForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            vname = cd['vname']
            key = ''.join([chr(random.randint(48, 122)) for i in range(20)])
            secret = hmac.new(key.encode('utf-8'), vname.encode('utf-8'), 'MD5').hexdigest()

            View(vname=cd['vname'], acl=cd['acl'], vremark=cd['vremark'], secret=secret).save()
            #form.save()
            audit = Audit(user=request.user.username, details='Add View: '+cd['vname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('view'))
    else:
        item_en = 'Add View'
        item_ch = '增加视图'
        form = ViewForm()
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def delete_view(request, view_id):
    view = View.objects.get(id=view_id)
    if request.method == 'POST':
        href = ''
        message = 'init'
        if Record.objects.filter(view=view_id):
            message = 'The view have record !'
            return render(request, 'confirm.html', {'message': message, 'href': href})

        view.delete()
        audit = Audit(user=request.user.username, details='Delete View: '+view.vname)
        audit.save()
        return HttpResponseRedirect(reverse('view'))

    else:
        item_en = 'Delete View'
        item_ch = '删除视图'
        form = ViewForm(instance=view)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def edit_view(request, view_id):
    view = View.objects.get(id=view_id)
    if request.method == 'POST':
        form = ViewForm(request.POST, instance=view)
        if form.is_valid():
            form.save()
            cd = form.cleaned_data
            audit = Audit(user=request.user.username, details='Edit View: '+cd['vname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('view'))
    else:
        item_en = 'Edit View'
        item_ch = '编辑视图'
        form = ViewForm(instance=view)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def zone(request):
    if request.method == 'GET':
        results = Zone.objects.all()
        return render(request, 'smartdns/zone.html', {'results': results})


@login_required
def add_zone(request):
    if request.method == 'POST':
        form = ZoneForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            audit = Audit(user=request.user.username, details='Add Zone: '+cd['zname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('zone'))
    else:
        item_en = 'Add Zone'
        item_ch = '增加域'
        form = ZoneForm()
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def delete_zone(request, zone_id):
    zone = Zone.objects.get(id=zone_id)
    if request.method =='POST':
        href = ''
        message = 'init'

        if Record.objects.filter(zone=zone_id):
            message = 'The zone have record !'
            return render(request, 'confirm.html', {'message': message, 'href': href})

        zone.delete()
        audit = Audit(user=request.user.username, details='Delete Zone: '+zone.zname)
        audit.save()
        return HttpResponseRedirect(reverse('zone'))

    else:
        item_en = 'Delete Zone'
        item_ch = '删除域'
        form = ZoneForm(instance=zone)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def edit_zone(request, zone_id):
    zone = Zone.objects.get(id=zone_id)
    if request.method == 'POST':
        form = ZoneForm(request.POST, instance=zone)
        if form.is_valid():
            cd = form.cleaned_data
            form.save()
            audit = Audit()
            audit.user = request.user.username
            audit.details = 'Edit Zone: '+cd['zname']
            #audit = Audit(user=request.user.username, details='Edit Zone: '+cd['zname'])
            audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(reverse('zone'))
    else:
        item_en = 'Edit Zone'
        item_ch = '修改域'
        form = ZoneForm(instance=zone)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def record(request):
    if request.method == 'GET':
        data = Zone.objects.all()

        ## defaultdict method (multidict)
        #results = defaultdict(set)
        #for i in data:
        #    for a in i.view.all():
        #        results[i].add(a)
        #results = dict(results)
        #print(type(results), results)

        results = {}
        for i in data:
            if i not in results:
                results[i] = []
            for a in i.view.all():
                count_result = Record.objects.filter(zone=i, view=a).count()
                d = [a, count_result]
                results[i].append(d)

        ## dict method (multidict)
        #results = {}
        #for i in data:
        #    if i.zname not in results:
        #        results[i.zname] = []
        #    for a in i.view.all():
        #        results[i.zname].append(a.vname)

        return render(request, 'smartdns/record.html', {'results': results})


@login_required
def record_detail(request, zone_id, view_id):
    if request.method == 'GET':
        zone = Zone.objects.get(id=zone_id)
        view = View.objects.get(id=view_id)
        results = Record.objects.filter(zone=zone, view=view)
        return render(request, 'smartdns/record_detail.html', {'results': results, 'zone': zone , 'view': view})


@login_required
def add_record_null(request):
    if request.method == 'POST':
        form = RecordForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            url = reverse('record')
            href = ''
            message = 'init'

            if not Zone.objects.filter(zname=cd['zone'], view__vname=cd['view']):
                message = "domain and view don't match !"
                return render(request, 'confirm.html', {'message': message, 'href': href})

            if Record.objects.filter(rname=cd['rname'], rdtype=cd['rdtype'],
                                     rdata=cd['rdata'], view=cd['view'], zone=cd['zone']):
                message = "this record is repeated !"
                return render(request, 'confirm.html', {'message': message, 'href': href})

            # If the check passes
            # record
            data = Server.objects.filter(sname='master')
            keyring = dns.tsigkeyring.from_text({cd['view'].vname: cd['view'].secret})
            up = dns.update.Update(cd['zone'].zname, keyring=keyring)
            up.add(cd['rname'], cd['ttl'], cd['rdtype'], cd['rdata'])
            for i in data:
                host_m = Server.objects.get(sname='master', cluster=i.cluster).ip
                dns.query.tcp(up, host_m)

            # mysql
            form.save()
            audit = Audit(user=request.user.username, details='ADD | Zone: '+cd['zone'].zname+' | View: '+cd['view'].vname+' | Record: '+cd['rname']+' '+cd['rdtype']+' '+cd['rdata']+' '+str(cd['ttl']))
            audit.save()

        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(url)

    else:
        item_en = 'Add Record'
        item_ch = '增加记录'
        form = RecordForm()
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def add_record(request, zone_id, view_id):
    if request.method == 'POST':
        form = RecordForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            url = reverse('record_detail', kwargs={'zone_id': cd['zone'].id, 'view_id': cd['view'].id})
            href = ''
            message = 'init'

            if not Zone.objects.filter(zname=cd['zone'], view__vname=cd['view']):
                message = "domain and view don't match !"
                return render(request, 'confirm.html', {'message': message, 'href': href})

            if Record.objects.filter(rname=cd['rname'], rdtype=cd['rdtype'],
                                     rdata=cd['rdata'], view=cd['view'], zone=cd['zone']):
                message = "this record is repeated !"
                return render(request, 'confirm.html', {'message': message, 'href': href})

            # If the check passes
            # record
            data = Server.objects.filter(sname='master')
            keyring = dns.tsigkeyring.from_text({cd['view'].vname: cd['view'].secret})
            up = dns.update.Update(cd['zone'].zname, keyring=keyring)
            up.add(cd['rname'], cd['ttl'], cd['rdtype'], cd['rdata'])
            for i in data:
                host_m = Server.objects.get(sname='master', cluster=i.cluster).ip
                dns.query.tcp(up, host_m)

            # mysql
            form.save()
            audit = Audit(user=request.user.username, details='ADD | Zone: '+cd['zone'].zname+' | View: '+cd['view'].vname+' | Record: '+cd['rname']+' '+cd['rdtype']+' '+cd['rdata']+' '+str(cd['ttl']))
            audit.save()

        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(url)
    else:
        item_en = 'Add Record'
        item_ch = '增加记录'
        form = RecordForm(initial={'zone':zone_id, 'view':view_id})
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def delete_record(request, zone_id, view_id, record_id):
    record = Record.objects.get(id=record_id)

    if request.method == 'POST':
        form = RecordForm(request.POST)
        zone = Zone.objects.get(id=zone_id)
        view = View.objects.get(id=view_id)
        record = Record.objects.get(id=record_id)
        url = reverse('record_detail', kwargs={'zone_id': zone_id, 'view_id': view_id})

        # record
        data = Server.objects.filter(sname='master')
        keyring = dns.tsigkeyring.from_text({view.vname: view.secret})
        up = dns.update.Update(zone.zname, keyring=keyring)
        up.delete(record.rname, record.rdtype, record.rdata)
        for i in data:
            host_m = Server.objects.get(sname='master', cluster=i.cluster).ip
            dns.query.tcp(up, host_m)

        # mysql
        record.delete()
        audit = Audit(user=request.user.username, details='Delete | Zone: '+zone.zname+' | View: '+view.vname+' | Record: '+record.rname+' '+record.rdtype+' '+record.rdata+' '+str(record.ttl))
        audit.save()

        return HttpResponseRedirect(url)

    else:
        item_en = 'Delete Record'
        item_ch = '删除记录'
        form = RecordForm(instance=record)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def edit_record(request, zone_id, view_id, record_id):
    record = Record.objects.get(id=record_id)
    zone = Zone.objects.get(id=zone_id)
    view = View.objects.get(id=view_id)

    if request.method == 'POST':
        form = Edit_RecordForm(request.POST, instance=record)

        if form.is_valid():
            cd = form.cleaned_data
            #url = reverse('record_detail', kwargs={'zone_id': cd['zone'].id, 'view_id': cd['view'].id})
            url = reverse('record_detail', kwargs={'zone_id': zone_id, 'view_id': view_id})
            href = ''
            message = 'init'

            #if not Zone.objects.filter(zname=cd['zone'], view__vname=cd['view']):
            #    message = 'The View not have this Zone !'
            #    return render(request, 'confirm.html', {'message': message, 'href': href})

            #if Record.objects.filter(rname=cd['rname'], rdtype=cd['rdtype'],
            #                         rdata=cd['rdata'], ttl=cd['ttl'], view=cd['view'], zone=cd['zone']):
            if Record.objects.filter(rname=cd['rname'], rdtype=cd['rdtype'],
                                     rdata=cd['rdata'], ttl=cd['ttl'], view=view_id, zone=zone_id):
                message = "this record is repeated !"
                return render(request, 'confirm.html', {'message': message, 'href': href})

            # If the check passes
            # record: Insert DNS records after deletion 
            #zone = Zone.objects.get(id=zone_id)
            #view = View.objects.get(id=view_id)
            record = Record.objects.get(id=record_id)
            data = Server.objects.filter(sname='master')
            keyring = dns.tsigkeyring.from_text({view.vname: view.secret})
            up = dns.update.Update(zone.zname, keyring=keyring)
            up.delete(record.rname, record.rdtype, record.rdata)
            up.add(cd['rname'], cd['ttl'], cd['rdtype'], cd['rdata'])
            for i in data:
                host_m = Server.objects.get(sname='master', cluster=i.cluster).ip
                dns.query.tcp(up, host_m)

            # mysql
            form.save()
            audit = Audit(user=request.user.username, details='Edit | Zone: '+zone.zname+' | View: '+view.vname+' | Record: '+cd['rname']+' '+cd['rdtype']+' '+cd['rdata']+' '+str(cd['ttl']))
            audit.save()

        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(url)

    else:
        href = ''
        message = 'init'
        if not Record.objects.filter(id=record_id, view=view_id, zone=zone_id):
                message = "This record does not exist !"
                return render(request, 'confirm.html', {'message': message, 'href': href})
        item_en = 'Edit Record'
        item_ch = '修改记录'
        form = Edit_RecordForm(instance=record)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch, 'zone': zone, 'view':view })


@login_required
def record_note(request, zone_id, view_id, record_id):
    record = Record.objects.get(id=record_id)
    if request.method == 'POST':
        form = RecordNoteForm(request.POST, instance=record)
        if form.is_valid():
            cd = form.cleaned_data
            url = reverse('record_detail', kwargs={'zone_id': zone_id, 'view_id': view_id})
            zone = Zone.objects.get(id=zone_id)
            view = View.objects.get(id=view_id)
            form.save()
            #audit = Audit(user=request.user.username, 
            #              details='RecordNote | Zone: '+zone.zname+' | View: '+view.vname+' | Record: '+record.rname+' | Note: '+cd['rremark'])
            #audit.save()
        else:
            print(form.errors.as_json())
        return HttpResponseRedirect(url)
    else:
        item_en = 'Record Note'
        item_ch = '记录备注'
        form = RecordNoteForm(instance=record)
    return render(request, 'smartdns/form.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def input_record(request, zone_id, view_id):
    if request.method == 'POST':
        # 上传的文件存储在request.FILES中
        # f.read()是从文件中读取整个上传的数据。如果上载的文件很大，将会占用大量内存，可使用chunks()代替。
        form = RcdUploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            f = request.FILES['file']
            # 获取文件格式
            type_excel = f.name.split('.')[-1]
            href = ''
            message = 'init'
            print ('----type_excel', type_excel)

            if type_excel != 'xls':
                message = '上传文件格式不是xls'
                return render(request, 'confirm.html', {'message': message, 'href': href})

            if f.size >= 2097152:
                message = '文件大于2MB'
                return render(request, 'confirm.html', {'message': message, 'href': href})

            # 开始解析上传的excel表格
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())
            table = wb.sheets()[0]
            nrows = table.nrows  # 行数
            #ncole = table.ncols  # 列数
            #print("row :%s, cole: %s" % (nrows, ncole))

            if nrows > 500:
                message = '记录数目大于500'
                return render(request, 'confirm.html', {'message': message, 'href': href})

            # 获取跳转页面的url
            #url = reverse('record_detail', kwargs={'zone_id': zone_id, 'view_id': view_id})

            # 获取DNS记录对应的视图和域对象
            zone = Zone.objects.get(id=zone_id)
            view = View.objects.get(id=view_id)
            # 初始化计数器
            x = y = z = 0

            for i in range(1, nrows):
                rowValues = table.row_values(i)  # 一行数据
                # rowValues[0] rname, rowValues[1] rdtype, rowValues[2] rdata
                # rowValues[3] TTL, rowValues[4] remark
                print('**********')
                print(rowValues)
                
                if rowValues[0] == '' or rowValues[1] == '' or rowValues[2] == '' or rowValues[3] == '':
                    print('-------------------------------------------')
                    z += 1
                    continue
                
                if Record.objects.filter(rname=rowValues[0], rdtype=rowValues[1], 
                                         rdata=rowValues[2], view=view, zone=zone):
                    y += 1
                    continue

                #rowValues[3] = int(rowValues[3])  # TTL must be int
                # dnspython
                data = Server.objects.filter(sname='master')
                keyring = dns.tsigkeyring.from_text({view.vname: view.secret})
                up = dns.update.Update(zone.zname, keyring=keyring)
                up.add(rowValues[0], rowValues[3], rowValues[1], rowValues[2])
                for i in data:
                    host_m = Server.objects.get(sname='master', cluster=i.cluster).ip
                    dns.query.tcp(up, host_m)
                # Model Record
                record = Record(rname=rowValues[0], rdtype=rowValues[1], 
                                rdata=rowValues[2], ttl=rowValues[3], 
                                rremark=rowValues[4], view=view, zone=zone)
                record.save()
                # Model Audit
                audit = Audit(user=request.user.username, details='Edit | Zone: '+zone.zname+' | View: '+view.vname+' | Record: '+rowValues[0]+' '+rowValues[1]+' '+rowValues[2]+' '+str(rowValues[3]))
                audit.save()
                x += 1  #插入条数

            message = 'Insert: %s | Duplicate: %s | Empty: %s' %(x, y, z)

        else:
            print(form.errors.as_json())
        return render(request, 'succeed_confirm.html', {'message': message, 'href': href})

    else:
        item_en = 'Batch Add Record'
        item_ch = '批量添加记录'
        form = RcdUploadFileForm()
    return render(request, 'smartdns/batch_add_batch.html', {'form': form, 'item_en': item_en, 'item_ch': item_ch})


@login_required
def output_record(request, zone_id, view_id):
    # 获取DNS记录对应的视图和域对象
    zone = Zone.objects.get(id=zone_id)
    view = View.objects.get(id=view_id)
    # Excel处理
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename='+zone.zname+'_'+view.vname+'.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('record')
    # 1st line
    sheet.write(0, 0, '主机记录')
    sheet.write(0, 1, '记录类型')
    sheet.write(0, 2, '记录值')
    sheet.write(0, 3, 'TTL(s)')
    sheet.write(0, 4, '备注')

    results = Record.objects.filter(view=view, zone=zone)
    excel_row = 1

    for result in results:
        sheet.write(excel_row, 0, result.rname)
        sheet.write(excel_row, 1, result.rdtype)
        sheet.write(excel_row, 2, result.rdata)
        sheet.write(excel_row, 3, result.ttl)
        sheet.write(excel_row, 4, result.rremark)
        excel_row += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    response.write(output.getvalue())
    return response


@login_required
def audit(request):
    if request.method == 'GET':
        results = Audit.objects.all()
        return render(request, 'smartdns/audit.html', {'results': results})


@login_required
def help(request):
    if request.method == 'GET':
        return render(request, 'smartdns/help.html')

def display_meta(request):
    values = request.META.items()
    client_ip = request.META['HTTP_X_CLIENT_IP']
    print(client_ip)
    #values.sort()
    rest = sorted(values)
    html = []
    #for k, v in values:
    for k, v in rest:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))
