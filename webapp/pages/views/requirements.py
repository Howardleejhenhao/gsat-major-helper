from django.shortcuts import render
from django.db import connection

def requirements(request):
    selected_univ_id = (request.GET.get("univ") or "").strip()
    selected_dept_id = (request.GET.get("dept") or "").strip()
    did_query = request.GET.get("q") == "1"

    universities = []
    departments = []

    summary_114 = None
    requirement_rows = []

    error = None

    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT univ_id, univ_name
                FROM University
                ORDER BY univ_id;
            """)
            universities = [{"univ_id": r[0], "univ_name": r[1]} for r in cur.fetchall()]
            if selected_univ_id:
                cur.execute("""
                    SELECT dept_id, dept_name
                    FROM Department
                    WHERE univ_id = %s
                    ORDER BY dept_id;
                """, [selected_univ_id])
                departments = [{"dept_id": r[0], "dept_name": r[1]} for r in cur.fetchall()]
            if did_query:
                if not selected_univ_id or not selected_dept_id:
                    error = "請先選擇學校與科系，再按查詢。"
                else:
                    # TODO: 114 summary_114
                    summary_114 = {}
                    # TODO: 歷年檢定標準
                    requirement_rows = []
                    pass

    except Exception as e:
        error = f"查詢發生錯誤：{e}"

    context = {
        "universities": universities,
        "departments": departments,
        "selected_univ_id": selected_univ_id,
        "selected_dept_id": selected_dept_id,
        "did_query": did_query,
        "summary_114": summary_114,
        "requirement_rows": requirement_rows,
        "error": error,
    }
    return render(request, "pages/requirements.html", context)
