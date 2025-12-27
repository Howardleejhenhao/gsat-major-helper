from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction

@csrf_exempt
@require_POST
def favorite_move(request):
    dept_id = (request.POST.get("dept_id") or "").strip()
    direction = (request.POST.get("direction") or "").strip()

    if not dept_id or direction not in ("up", "down"):
        return JsonResponse({"ok": False, "error": "bad params"}, status=400)

    with transaction.atomic():
        with connection.cursor() as cur:
            cur.execute("""
                SELECT sort_order
                FROM favorite
                WHERE dept_id = %s
                FOR UPDATE;
            """, [dept_id])
            row = cur.fetchone()
            if not row:
                return JsonResponse({"ok": False, "error": "not found"}, status=404)

            my_order = row[0]

            if direction == "up":
                cur.execute("""
                    SELECT dept_id, sort_order
                    FROM favorite
                    WHERE sort_order < %s
                    ORDER BY sort_order DESC
                    LIMIT 1
                    FOR UPDATE;
                """, [my_order])
            else:
                cur.execute("""
                    SELECT dept_id, sort_order
                    FROM favorite
                    WHERE sort_order > %s
                    ORDER BY sort_order ASC
                    LIMIT 1
                    FOR UPDATE;
                """, [my_order])

            nb = cur.fetchone()
            if not nb:
                return JsonResponse({"ok": True, "moved": False})

            nb_dept_id, nb_order = nb

            cur.execute("""
                UPDATE favorite
                SET sort_order = CASE
                    WHEN dept_id = %s THEN %s
                    WHEN dept_id = %s THEN %s
                    ELSE sort_order
                END
                WHERE dept_id IN (%s, %s);
            """, [dept_id, nb_order, nb_dept_id, my_order, dept_id, nb_dept_id])

    return JsonResponse({"ok": True, "moved": True})
