SELECT
  p.name,
  p.age,
  v.visit_date,
  COUNT(s.id) AS symptom_count
FROM patients AS p
JOIN visits AS v
  ON p.id = v.patient_id
LEFT JOIN symptoms AS s
  ON v.id = s.visit_id
WHERE
  v.department = 'Neurology' AND p.age > 50
GROUP BY
  p.name,
  p.age,
  v.visit_date
HAVING
  COUNT(s.id) >= 3
ORDER BY
  v.visit_date DESC
LIMIT 5;