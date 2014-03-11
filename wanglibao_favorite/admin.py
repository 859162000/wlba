from django.contrib import admin
from wanglibao_favorite.models import FavoriteTrust, FavoriteFinancing, FavoriteFund


admin.site.register(FavoriteTrust)
admin.site.register(FavoriteFund)
admin.site.register(FavoriteFinancing)

