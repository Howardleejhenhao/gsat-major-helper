"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from pages.views import home, score_conversion, standards_by_subject, category_compare
from pages.views.category_compare import toggle_favorite  # ⭐ 只新增這行
from pages.views.favorites import favorites

urlpatterns = [
    path('admin/', admin.site.urls),

    path("", home, name="home"),
    path("features/score-conversion/", score_conversion, name="score_conversion"),
    path("features/standards/", standards_by_subject, name="standards_by_subject"),
    path("features/category-compare/", category_compare, name="category_compare"),

    # ⭐ 收藏切換 API（只新增這段）
    path("api/favorite/toggle/", toggle_favorite, name="toggle_favorite"),
    path("features/favorites/", favorites, name="favorites"),

]

