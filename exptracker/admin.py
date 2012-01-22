from django.contrib import admin

from exptracker.models import SharedExpense, ExpenseItem, ExptrackerProfile #, Payment

class ExpenseItemInline(admin.TabularInline):
    model = ExpenseItem
    extra = 3

#class PaymentInline(admin.TabularInline):
#    model = Payment
#    list_display = ('recipient')
#    extra = 3

class SharedExpenseAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_date')
    	inlines = [ExpenseItemInline]

admin.site.register(SharedExpense, SharedExpenseAdmin)
admin.site.register(ExptrackerProfile)

