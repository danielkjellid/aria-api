from django.contrib import admin

from aria.employees.models import EmployeeInfo


@admin.register(EmployeeInfo)
class EmployeeInfoAdmin(admin.ModelAdmin):
    model = EmployeeInfo
    list_display = ("full_name", "company_email", "user")
