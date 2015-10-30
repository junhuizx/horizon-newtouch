"""
Stub file to work around django bug: https://code.djangoproject.com/ticket/7198
"""
from django.db import models
from django.utils import timezone

# Create your models here.

class Service(models.Model):
    name = models.CharField(max_length=32)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.create_time = timezone.now()
        self.update_time = timezone.now()
        return super(Service, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Server(models.Model):
    SNMP_VERSION_CHOICES = (
        ('1', '1'),
        ('2c', '2c'),
        ('3', '3'),
    )

    name = models.CharField(max_length=64)
    ip = models.CharField(max_length=64)
    create_time = models.DateTimeField(auto_now_add=True, editable=False)
    update_time = models.DateTimeField(editable=False)
    snmp_version = models.CharField(max_length=2, choices=SNMP_VERSION_CHOICES, default='2c')
    snmp_commit = models.CharField(max_length=32, default='public')
    ssh_name = models.CharField(max_length=32, default='root', null=True, blank=True)
    ssh_key = models.CharField(max_length=32, null=True, blank=True)
    services = models.ManyToManyField(Service, blank=True)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.create_time = timezone.now()
        self.update_time = timezone.now()
        return super(Server, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ServerMonitorMessage(models.Model):
    server = models.ForeignKey(Server)
    time = models.DateTimeField(auto_now_add=True, editable=False)
    cpu_usage = models.DecimalField(max_digits=4, decimal_places=2)
    mem_usage = models.DecimalField(max_digits=4, decimal_places=2)
    disk_usage = models.DecimalField(max_digits=4, decimal_places=2)
    process_num = models.IntegerField()
    process_status = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.time = timezone.now()
        self.time = timezone.now()
        return super(ServerMonitorMessage, self).save(*args, **kwargs)
