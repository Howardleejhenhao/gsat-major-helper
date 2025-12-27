from django.shortcuts import render
from django.db import connection

def favorites(request):
    sql = """
        SELECT
            u.univ_name,
            d.dept_name,
            c.academic_cluster,
            c.category_name,
            d.dept_id,
            f.sort_order
        FROM Favorite f
        JOIN Department d ON f.dept_id = d.dept_id
        JOIN University u ON d.univ_id = u.univ_id
        JOIN Category c ON d.category_id = c.category_id
        ORDER BY f.sort_order ASC;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    favorites = [
        {
            "univ_name": r[0],
            "dept_name": r[1],
            "academic_cluster": r[2],
            "category_name": r[3],
            "dept_id": r[4],
            "sort_order": r[5],
        }
        for r in rows
    ]

    return render(
        request,
        "pages/favorites.html",
        {"favorites": favorites}
    )
