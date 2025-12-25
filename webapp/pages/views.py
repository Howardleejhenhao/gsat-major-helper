from django.shortcuts import render


def home(request):
    tags = [
        "五標級分", "級分轉換", "同類科系比較", "檢定標準", "收藏",
    ]

    features = [
        {
            "title": "查詢歷年五標級分",
            "desc": "依科目與年度查歷年五標／級分分布，快速掌握難度變化。",
            "meta": "科目 + 年分",
            "badge": "常用",
            "href": "/features/standards/",
            # icon: chart
            "icon_path": "M4 19V5M4 19h16M8 15v-3M12 15V9M16 15v-5",
        },
        {
            "title": "查詢歷年級分轉換",
            "desc": "用五標＋原始分數做級分推估，支援多年度比較趨勢。",
            "meta": "年分 + 多年比較",
            "badge": "比較",
            "href": "/features/score-conversion/",
            # icon: arrows
            "icon_path": "M7 7h10l-2-2M17 7l-2 2M17 17H7l2 2M7 17l2-2",
        },
        {
            "title": "同年度校系最低錄取分數比較",
            "desc": "列出同一 category_id 的校系，並比較同年度最低錄取分數。",
            "meta": "同類校系比較",
            "badge": "校系",
            "href": "/features/category-compare/",
            # icon: buildings
            "icon_path": "M7 21V3h10v18M9 7h2M9 11h2M9 15h2M13 7h2M13 11h2M13 15h2",
        },
        {
            "title": "同校同系歷年檢定標準",
            "desc": "查看同一校系歷年檢定門檻，並顯示當年對應到幾級分。",
            "meta": "校系 + 年分",
            "badge": "檢定",
            "href": "/features/requirements/",
            # icon: checklist
            "icon_path": "M9 6h11M9 12h11M9 18h11M4 6l1.2 1.2L7.5 5M4 12l1.2 1.2L7.5 11M4 18l1.2 1.2L7.5 17",
        },
        {
            "title": "我的最愛",
            "desc": "收藏常用校系、科目與查詢條件，下次一鍵打開並快速比對。",
            "meta": "學生收藏功能",
            "badge": "個人化",
            "href": "/features/favorites/",
            # icon: heart
            "icon_path": "M12 20s-7-4.5-7-10a4 4 0 0 1 7-2a4 4 0 0 1 7 2c0 5.5-7 10-7 10Z",
        },
    ]

    return render(request, "pages/home.html", {"tags": tags, "features": features})

def score_conversion(request):
    subjects = ["國文", "英文", "數A", "數B", "社會", "自然"]

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
                results = [
                    {"year": "111年", "level": "均標", "percent": "55.82", "range": "57.37＜X≦63.75"},
                    {"year": "112年", "level": "頂標", "percent": "17.58", "range": "63.75＜X≦70.12"},
                    {"year": "113年", "level": "前標", "percent": "31.26", "range": "57.43＜X≦63.81"},
                    {"year": "114年", "level": "均標", "percent": "32.67", "range": "63.75＜X≦70.19"},
                    {"year": "115年", "level": "均標", "percent": "32.67", "range": "63.75＜X≦70.19"},
                ]
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

def standards_by_subject(request):
    subjects = ["國文", "英文", "數A", "數B", "社會", "自然"]
    subject = request.GET.get("subject") or "數A"
    if subject not in subjects:
        subject = "數A"

    sql_query = """
    """.strip()

    mock_data = {
        "數A": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
        "國文": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
        "英文": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
        "數B": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
        "社會": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
        "自然": [
            {"year": 114, "top": 14, "front": 12, "avg": 10, "back": 8, "bottom": 6},
            {"year": 113, "top": 12, "front": 10, "avg": 7, "back": 5, "bottom": 3},
            {"year": 112, "top": 10, "front": 8, "avg": 6, "back": 4, "bottom": 2},
        ],
    }

    result_rows = mock_data.get(subject, [])

    return render(
        request,
        "pages/standards_by_subject.html",
        {
            "subjects": subjects,
            "subject": subject,
            "rows": result_rows,
        },
    )
