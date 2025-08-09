from django.contrib import admin
from .models import Makaleler, Mesaj, HakemDegerlendirme, EditorAtama

admin.site.register(Makaleler)
admin.site.register(Mesaj)
admin.site.register(HakemDegerlendirme)
admin.site.register(EditorAtama)