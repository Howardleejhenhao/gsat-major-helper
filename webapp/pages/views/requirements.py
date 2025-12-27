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

            if (not selected_univ_id) and selected_dept_id:
                cur.execute("""
                    SELECT univ_id
                    FROM Department
                    WHERE dept_id::text = %s
                    LIMIT 1;
                """, [selected_dept_id])
                row_u = cur.fetchone()
                if row_u:
                    selected_univ_id = str(row_u[0])

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
                    cur.execute("""
                    WITH combo AS (
                    SELECT
                        u.univ_name,
                        d.dept_name,
                        ar.exam_year,
                        ar.has_extra_screen,
                        sc.combo_order,
                        sc.combo_id,
                        STRING_AGG(s.subject_name, '+' ORDER BY cd.subject_id) AS subj_group,
                        MAX(cd.required_score) AS req_score
                    FROM AdmissionRecord ar
                    JOIN Department d ON d.dept_id = ar.dept_id
                    JOIN University u ON u.univ_id = d.univ_id
                    LEFT JOIN SubjectCombination sc ON sc.record_id = ar.record_id
                    LEFT JOIN CombinationDetail cd ON cd.combo_id = sc.combo_id
                    LEFT JOIN Subject s ON s.subject_id = cd.subject_id
                    WHERE ar.dept_id::text = %s
                        AND ar.exam_year::text = '114'
                    GROUP BY
                        u.univ_name, d.dept_name, ar.exam_year, ar.has_extra_screen,
                        sc.combo_order, sc.combo_id
                    ),
                    yearly AS (
                    SELECT
                        univ_name,
                        dept_name,
                        exam_year,
                        MAX(has_extra_screen::int)::boolean AS has_extra_screen,
                        STRING_AGG(subj_group || '=' || req_score, '，' ORDER BY combo_order) AS standards
                    FROM combo
                    GROUP BY univ_name, dept_name, exam_year
                    )
                    SELECT univ_name, dept_name, standards, has_extra_screen
                    FROM yearly;
                    """, [selected_dept_id])

                    row = cur.fetchone()
                    if row:
                        summary_114 = {
                            "univ_name": row[0],
                            "dept_name": row[1],
                            "lowest_standard": row[2],
                            "has_extra_screen": row[3],
                        }
                    else:
                        summary_114 = None

                    # TODO: 歷年檢定標準
                    requirement_rows = []

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
