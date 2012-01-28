from django.contrib.admin import ModelAdmin as DjangoModelAdmin
from mptt.admin import MPTTModelAdmin as DjangoMPTTModelAdmin


class ModelAdmin(DjangoModelAdmin):
    pass

class MPTTModelAdmin(DjangoMPTTModelAdmin):
    pass
