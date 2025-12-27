from django.shortcuts import render
from django.db import connection

def standards_by_subject(request):
    subjects = ["國文", "英文", "數學A", "數學B", "社會", "自然"]
    subject = request.GET.get("subject") or "數A"
    if subject not in subjects:
        subject = "數A"

    sql_query = """
        SELECT 
            sl.exam_year,
            sl.top,
            sl.high,
            sl.avg,
            sl.low,
            sl.bottom
        FROM 
            StandardLevel sl
        JOIN 
            Subject s ON sl.subject_id = s.subject_id
        WHERE 
            s.subject_name = %s
        ORDER BY 
            sl.exam_year DESC;

    """.strip()

    with connection.cursor() as cursor:
        cursor.execute(sql_query, [subject])
        rows_db = cursor.fetchall()

    result_rows = [
        {
            "year": r[0],
            "top": r[1],
            "front": r[2],
            "avg": r[3],
            "back": r[4],
            "bottom": r[5],
        }
        for r in rows_db
    ]

    return render(
        request,
        "pages/standards_by_subject.html",
        {
            "subjects": subjects,
            "subject": subject,
            "rows": result_rows,
        },
    )
