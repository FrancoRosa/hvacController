# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib import admin



class Administrator(models.Model):
    name=models.CharField(max_length=25)
    phone=models.CharField(max_length=9, primary_key=True)
    email=models.CharField(max_length=50)
    
    class Meta:
        verbose_name_plural = "Administradores"

    def __str__(self):              # __unicode__ on Python 2
        return "%s"%(self.name)

class Building(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=25)
    addr = models.CharField(max_length=25)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    plan = models.FileField(upload_to='uploads/buildings/')
    
    class Meta:
        verbose_name_plural = "Edificios"


    def __str__(self):              # __unicode__ on Python 2
        return "%s"%(self.name)


class Floor(models.Model):
    #id = models.IntegerField(primary_key=True)
    building = models.ForeignKey(Building)
    level = models.IntegerField(default=1)
    admin=models.ForeignKey(Administrator)
    plan = models.FileField(upload_to='uploads/plans/')
    
    class Meta:
        verbose_name_plural = "Pisos"

    def __str__(self):              # __unicode__ on Python 2
        return "%s, Piso %s"%(self.building,self.level)


class Cooler(models.Model):
    LOW='Low'
    MED='Medium'
    HIG='High'
    ON='On'
    OFF='Off'
    SCH='Schedule'
    MAN='Manual'
    AUT='Autom'

    MOTOR_CHOICES=((OFF, 'Off'), (LOW, 'Low'), (MED, 'Medium'), (HIG, 'High'))
    POWERMODE_CHOICES=((ON, 'On'), (OFF, 'Off'), (SCH, 'Schedule'))
    CONTROLMODE_CHOICES=((MAN, 'Manual'), (AUT, 'Autom'))
    
    #id = models.IntegerField(primary_key=True)
    addr = models.IntegerField(default=0)
    name = models.CharField(max_length=25)
    floor = models.ForeignKey(Floor)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    fan = models.CharField(choices=MOTOR_CHOICES, max_length=10, default=OFF)
    valve = models.BooleanField(default=False)
    current = models.FloatField(default=0)
    target_temp = models.FloatField(default=21.0)
    target_hum = models.FloatField(default=50.0)
    temperature1 = models.FloatField(default=0)
    temperature2 = models.FloatField(default=0)
    temperature3 = models.FloatField(default=0)
    humidity1 = models.FloatField(default=0)
    input1 = models.BooleanField(default=False)
    input2 = models.BooleanField(default=False)
    powermode = models.CharField(choices=POWERMODE_CHOICES, max_length=10, default=SCH)
    controlmode = models.CharField(choices=CONTROLMODE_CHOICES, max_length=10, default=AUT)

    class Meta:
        verbose_name_plural = "HVAC"

    def __str__(self):              # __unicode__ on Python 2
        return "%s, %s"%(self.floor,self.name)


class Schedule(models.Model):
    DAYS_OF_WEEK = (('0', 'Monday'),
                    ('1', 'Tuesday'),
                    ('2', 'Wednesday'),
                    ('3', 'Thursday'),
                    ('4', 'Friday'),
                    ('5', 'Saturday'),
                    ('6', 'Sunday'))

    cooler = models.ForeignKey(Cooler)
    #building = models.ForeignKey(Building)
    #floor = models.ForeignKey(Floor)
    day = models.CharField(max_length=1, choices=DAYS_OF_WEEK)
    s_start = models.TimeField("Begin",default="07:00:00")
    s_stop = models.TimeField("End",default="19:00:00")

    class Meta:
        verbose_name_plural = "Horarios"

    def __str__(self):              # __unicode__ on Python 2
        return "%s"%(self.DAYS_OF_WEEK[int(self.day)][1])

class Alert(models.Model):
    cooler = models.ForeignKey(Cooler)
    a_date = models.DateField()
    a_time = models.TimeField()
    message = models.CharField(max_length=50, default="Revisar Conexión de Motor")
    send = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Alertas"
