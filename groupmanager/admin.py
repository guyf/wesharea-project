from django.contrib import admin
from groupmanager.models import *


class InvitationInline(admin.TabularInline):
    model = Invitation
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    	inlines = [InvitationInline]

admin.site.register(Group, GroupAdmin)

