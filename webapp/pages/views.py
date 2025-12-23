from django.db import connection
from django.shortcuts import render


def home(request):
    with connection.cursor() as cur:
        cur.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_schema, table_name;
        """)
        tables = cur.fetchall()

    return render(request, "pages/home.html", {"tables": tables})
