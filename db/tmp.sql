SELECT
    u.univ_name,
    d.dept_name,
    c.academic_cluster,
    c.category_name
FROM Favorite f
JOIN Department d
    ON f.dept_id = d.dept_id
JOIN University u
    ON d.univ_id = u.univ_id
JOIN Category c
    ON d.category_id = c.category_id;
