from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
def category_compare(request):

    # ====== 1. 取得學群 ======
    get_clusters_sql = """
        SELECT DISTINCT academic_cluster
        FROM Category;
    """.strip()

    with connection.cursor() as cursor:
        cursor.execute(get_clusters_sql)
        clusters = cursor.fetchall()

    clusters = [s[0] for s in clusters]

    # ====== 2. 依學群取得學類 ======
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

        categories = [s[0] for s in categories]

    # ====== 3. 依學類取得查詢結果 ======
    selected_category = request.GET.get("category") or ""

    get_results_sql = """
        SELECT 
            u.univ_name, --學校名稱
            d.dept_name, --科系名稱
            d.dept_id,
            STRING_AGG(
                CONCAT(s.subject_name, '=', cd.required_score), 
                ', ' 
                ORDER BY sc.combo_order ASC
            ), --篩選標準詳情
            ar.has_extra_screen --超篩有無
        FROM 
            AdmissionRecord ar
        JOIN 
            Department d ON ar.dept_id = d.dept_id
        JOIN 
            University u ON d.univ_id = u.univ_id
        JOIN 
            Category c ON d.category_id = c.category_id
        JOIN 
            SubjectCombination sc ON ar.record_id = sc.record_id
        JOIN 
            CombinationDetail cd ON sc.combo_id = cd.combo_id
        JOIN 
            Subject s ON cd.subject_id = s.subject_id
        WHERE 
            c.category_name = %s
            AND ar.exam_year = '114'
        GROUP BY 
            u.univ_id, d.dept_id, u.univ_name, d.dept_name, ar.lowest_total, ar.has_extra_screen
        ORDER BY 
            u.univ_id ASC;
    """.strip()
    results = []
    if selected_category:
        with connection.cursor() as cursor:
            cursor.execute(get_results_sql, [selected_category])
            rows = cursor.fetchall()

        results = [
            {
                "univ_name": r[0],
                "dept_name": r[1],
                "dept_id": r[2],
                "lowest_total": r[3],
                "has_extra_screen": r[4],
            }
            for r in rows
        ]

    # ====== 4. ★★ 這裡加入「已收藏的 dept_id」 ★★ ======
    get_favorites_sql = """
        SELECT dept_id
        FROM Favorite;
    """

    with connection.cursor() as cursor:
        cursor.execute(get_favorites_sql)
        favorite_depts = {row[0] for row in cursor.fetchall()}

    # ====== 5. 組 context ======
    context = {
        "clusters": clusters,
        "selected_cluster": selected_cluster,
        "categories": categories,
        "selected_category": selected_category,
        "results": results,
        "favorite_depts": favorite_depts,   # ★ 丟給 template
    }

    return render(request, "pages/category_compare.html", context)


@csrf_exempt
@require_POST
def toggle_favorite(request):
    dept_id = request.POST.get("dept_id")
    if not dept_id:
        return JsonResponse({"error": "missing dept_id"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM Favorite WHERE dept_id = %s;",
            [dept_id]
        )
        exists = cursor.fetchone()

        if exists:
            cursor.execute(
                "DELETE FROM Favorite WHERE dept_id = %s;",
                [dept_id]
            )
            favorited = False
        else:
            cursor.execute(
                "INSERT INTO Favorite (dept_id) VALUES (%s);",
                [dept_id]
            )
            favorited = True

    return JsonResponse({"favorited": favorited})

