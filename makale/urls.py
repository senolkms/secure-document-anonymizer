from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

app_name = 'makale'

urlpatterns = [
    path('', views.ana_sayfa, name='anasayfa'),  # Ana sayfa
    path('makale_yukle/', views.makale_yukleme_sayfasi, name='makale_yukleme_sayfasi'),  # HTML sayfasını göster
    path('yukle/api/', views.makale_yukle, name='makale_yukle'),  # Makale yükleme işlemi
    path('makale_sorgula/', views.makale_sorgulama_sayfasi, name='makale_sorgulama_sayfasi'),
    path('makale_sorgula/api/', views.makale_sorgula, name='makale_sorgula'),
    path('mesaj_gonder/', views.mesaj_gonderme_sayfasi, name='mesaj_gonderme_sayfasi'),
    path('mesaj_gonder/api/', views.mesaj_gonder, name='mesaj_gonder'),
    path('editor_panel/', views.editor_paneli, name='editor_panel'),
    path('anonimlestir/', views.anonimlestir_makale, name='anonimlestir_makale'),
    path('alan_atama/', views.alan_atama, name='alan_atama'),
    path('makale_detay/', views.makale_detay, name='makale_detay'),
    path('hakeme_ata/', views.hakeme_ata, name='hakeme_ata'),
    path('hakem_giris/', views.hakem_giris, name='hakem_giris'),
    path('hakem_panel/', views.hakem_panel, name='hakem_panel'),
    path("hakem_degerlendir/", views.hakem_degerlendir, name="hakem_degerlendir"),
    path("desifre_et/", views.desifre_et, name="desifre_et"),
    path("editor_mesaj/", views.editor_mesaj, name="editor_mesaj"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
