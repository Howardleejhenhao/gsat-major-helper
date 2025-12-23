SELECT COUNT(*) AS orphan_admissionrecord_dept
FROM admissionrecord ar
LEFT JOIN department d ON d.dept_id = ar.dept_id
WHERE d.dept_id IS NULL;
