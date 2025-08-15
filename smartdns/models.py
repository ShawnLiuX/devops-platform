from django.db import models
import django.utils.timezone as timezone


class Cluster(models.Model):
    cname = models.CharField('名称', max_length=50, unique=True)
    cremark = models.CharField('备注', max_length=50, blank=True)

    class Meta:
        db_table = 'smartdns_cluster'

    def __str__(self):
        return self.cname


class Server(models.Model):
    type = (
        ('master', '权威'),
        ('slave', '边缘'),
        ('cache', '缓存'),
    )
    sname = models.CharField('服务器', max_length=20, choices=type, default='权威')
    ip = models.CharField('IP地址', max_length=20)
    sremark = models.CharField('备注', max_length=20, blank=True)
    cluster = models.ForeignKey(Cluster, on_delete=models.PROTECT)

    class Meta:
        db_table = 'smartdns_server'

    def __str__(self):
        return self.sname


class View(models.Model):
    vname = models.CharField('名称', max_length=20, unique=True)
    acl = models.TextField('ACL', max_length=1000)
    vremark = models.CharField('描述', max_length=50)
    secret = models.CharField('KEY', max_length=50)

    class Meta:
        db_table = 'smartdns_view'

    def __str__(self):
        return self.vname


class Zone(models.Model):
    zname = models.CharField('名称', max_length=20, unique=True)
    zremark = models.CharField('描述', max_length=50)
    view = models.ManyToManyField(View, through='zone_view', blank=True)

    class Meta:
        db_table = 'smartdns_zone'

    def __str__(self):
        return self.zname

    def view_list(self):
        return ' '.join([i.vname for i in self.view.all()])


class zone_view(models.Model):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    view = models.ForeignKey(View, on_delete=models.CASCADE)
    #zone = models.ForeignKey(Zone, on_delete=models.PROTECT)
    #view = models.ForeignKey(View, on_delete=models.PROTECT)

    class Meta:
        db_table = 'smartdns_zone_view'


class Record(models.Model):
    type = (
        ('A', 'A'),
        ('CNAME', 'CNAME'),
        ('NS', 'NS'),
    )
    rname = models.CharField('主机记录', max_length=50)
    rdtype = models.CharField('记录类型', max_length=5, choices=type, default='A')
    rdata = models.CharField('记录值', max_length=50)
    ttl = models.IntegerField('TTL(s)', default='600')
    rremark = models.CharField('备注', max_length=50, blank=True)
    view = models.ForeignKey(View, on_delete=models.PROTECT, verbose_name='视图')
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, verbose_name='域')
    add_date = models.DateTimeField('保存日期', default = timezone.now)
    mod_date = models.DateTimeField('最后修改日期', auto_now=True)

    class Meta:
        db_table = 'smartdns_record'

    def __str__(self):
        return self.rname


class Audit(models.Model):
    user = models.CharField(max_length=30)
    details = models.CharField(max_length=200)
    add_date = models.DateTimeField('保存日期', auto_now_add=True)

    class Meta:
        db_table = 'smartdns_audit'

    def __str__(self):
        return self.details

