# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import Room
from .models import Status

from .models import Administrator
from .models import Building
from .models import Floor
from .models import Cooler
from .models import Schedule
from .models import Alert


class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_name','floor_name','modbus_id')
    list_filter = ('modbus_id', 'floor_name') 
    search_fields = ('room_name','modbus_id')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('room','nivel_1','nivel_2','nivel_3','light','temperature')
    list_editable = ('nivel_1','nivel_2','nivel_3','light')
    list_filter = ('room','temperature') 
    search_fields = ('room','temperature')

#admin.site.register(Room, RoomAdmin)
#admin.site.register(Status, StatusAdmin)

class AdministratorAdmin(admin.ModelAdmin):
    list_display = ('name','phone','email')
    list_filter = ('name','phone') 
    search_fields = ('name','phone')

class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name','addr')
    list_filter = ('name','addr') 
    search_fields = ('name','addr')

class FloorAdmin(admin.ModelAdmin):
    list_display = ('building','level','admin')
    list_filter = ('building','admin') 
    search_fields = ('building','admin')

class CoolerAdmin(admin.ModelAdmin):
    list_display = ('name','floor','addr','temperature1','humidity1','fan','valve','powermode','controlmode')
    list_filter = ('floor','temperature1')
    list_editable = ('fan','valve','powermode','controlmode') 
    search_fields = ('floor','name')

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('cooler','day','s_start','s_stop')
    list_filter = ('cooler','day') 
    search_fields = ('cooler','day')

class AlertAdmin(admin.ModelAdmin):
    list_display = ('cooler','a_date','a_time','message','send')
    list_filter = ('cooler','a_date')
    search_fields = ('cooler','a_date')

admin.site.register(Administrator, AdministratorAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Floor, FloorAdmin)
admin.site.register(Cooler, CoolerAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Alert, AlertAdmin)

