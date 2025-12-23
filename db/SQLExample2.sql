SELECT
  d.dept_id,
  d.dept_name,
  c.academic_cluster,
  c.category_name
FROM department d
JOIN category c ON c.category_id = d.category_id
LIMIT 20;
