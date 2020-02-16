from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Datasource
from .models import Search
from .models import Value

admin.site.register(Datasource)
admin.site.register(Search)
admin.site.register(Value)