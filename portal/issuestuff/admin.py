from django.contrib import admin
from issuestuff.models import Member,Log,IssuingLog,Stuff

class MemberAdmin(admin.ModelAdmin):
	list_display = ('user','roll','email','roll','sex','contact','hostel','discipline','join_year','graduation_year','degree','current_status','current_log')

class LogAdmin(admin.ModelAdmin):
	list_display=('user','intime','outtime')

class IssuingLogAdmin(admin.ModelAdmin):
	list_display = ('user','stuff','quantity','taketime','returntime')	

class StuffAdmin(admin.ModelAdmin):
	list_display = ('name',)	
# Register your models here.



admin.site.register(Member,MemberAdmin)
admin.site.register(Log,LogAdmin)
admin.site.register(IssuingLog,IssuingLogAdmin)
admin.site.register(Stuff,StuffAdmin)
