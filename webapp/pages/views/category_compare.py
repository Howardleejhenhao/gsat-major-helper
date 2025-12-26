from django.shortcuts import render
from django.db import connection

def category_compare(request):
    
    get_clusters_sql = """
        SELECT DISTINCT academic_cluster
        FROM Category;
    """.strip()

    with connection.cursor() as cursor:
        cursor.execute(get_clusters_sql)
        clusters = cursor.fetchall()
    clusters = [
        s[0] for s in clusters
    ]

    selected_cluster = request.GET.get("cluster") or ""
    get_categories_sql = """
        SELECT category_name
        FROM Category
        WHERE academic_cluster = %s;
    """.strip()
    categories = []
    if selected_cluster:
        with connection.cursor() as cursor:
            cursor.execute(get_categories_sql, [selected_cluster])
            categories = cursor.fetchall()
        categories = [
            s[0] for s in categories
        ]

    selected_category = request.GET.get("category") or ""
    get_results_sql = """
        SELECT 
            u.univ_name,
            d.dept_name,
            ar.lowest_total,
            ar.has_extra_screen
        FROM 
            AdmissionRecord ar
        JOIN 
            Department d ON ar.dept_id = d.dept_id
        JOIN 
            University u ON d.univ_id = u.univ_id
        JOIN 
            Category c ON d.category_id = c.category_id
        WHERE 
            c.category_name = %s
            AND ar.exam_year = '114'
        ORDER BY 
            u.univ_id ASC;
    """
    results = []
    if selected_category:
        with connection.cursor() as cursor:
            cursor.execute(get_results_sql, [selected_category])
            results = cursor.fetchall()
        results = [
            {
                "univ_name": s[0],
                "dept_name": s[1],
                "lowest_total": s[2],
                "has_extra_screen": s[3],
            }
            for s in results
        ]


    context = {
        "clusters": clusters,
        "selected_cluster": selected_cluster,
        "categories": categories,
        "selected_category": selected_category,
        "results": results,
    }
    return render(request, "pages/category_compare.html", context)