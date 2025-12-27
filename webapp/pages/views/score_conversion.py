from django.shortcuts import render
from django.db import connection

def score_conversion(request):
    subjects = ["國文", "英文", "數學A", "數學B", "社會", "自然"]

    subject = request.GET.get("subject", "國文")
    score_raw = request.GET.get("score", "").strip()

    score = None
    error = None
    results = None

    if score_raw != "":
        try:
            score = int(score_raw)
            if score < 0 or score > 15:
                error = "級分請輸入 0～15 之間的整數"
            else:
                sql = """
                    WITH input AS (
                    SELECT

                        %s::varchar AS sub_name,
                        %s::int            AS lvl
                    )
                    SELECT
                    sp.exam_year AS year,
                    CASE
                        WHEN input.lvl >= sl.top    THEN '頂標'
                        WHEN input.lvl >= sl.high   THEN '前標'
                        WHEN input.lvl >= sl.avg    THEN '均標'
                        WHEN input.lvl >= sl.low    THEN '後標'
                        WHEN input.lvl >= sl.bottom THEN '底標'
                        ELSE '流標'
                    END AS standard,
                    sp.percentile AS percentile,
                    sp.min_score AS range_low,
                    sp.max_score AS range_high
                    FROM input
                    JOIN Subject sub
                    ON sub.subject_name = input.sub_name
                    JOIN SubjectPerformance sp
                    ON sp.subject_id = sub.subject_id
                    AND sp.level = input.lvl
                    JOIN StandardLevel sl
                    ON sl.exam_year = sp.exam_year
                    AND sl.subject_id = sub.subject_id
                    ORDER BY sp.exam_year;
                    """
                with connection.cursor() as cur:
                    cur.execute(sql, [subject, score])
                    rows = cur.fetchall()
                results = []
                for year, standard, percent, low, high, in rows:
                    results.append({
                        "year": f"{year}年",
                        "level": standard,
                        "percent": f"{percent:.2f}",
                        "range": f"{low}＜X≦{high}",

                    })

        except ValueError:
            error = "級分請輸入整數（例如 10）"

    context = {
        "subjects": subjects,
        "subject": subject,
        "score_raw": score_raw,
        "score": score,
        "error": error,
        "results": results,
    }
    return render(request, "pages/score_conversion.html", context)
