-- gases plot 1
SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '2024-09-12'::timestamp AS start_time, '2024-09-13'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, co2_l, co2_p, co2_e,round(ocs * 1000000,0)::float8 AS ocs, co2_pic, ch4_pic FROM (
    SELECT DISTINCT ON (dt) dt AS datetime, co2 AS co2_p FROM (
        SELECT date_trunc('minute',datetime) AS dt, co2
        FROM bor__lic7000_p_v0
         WHERE co2 IS NOT NULL
        AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ORDER BY datetime
    ) AS subq_profile1
) AS subq_profile
FULL JOIN (
    SELECT DISTINCT ON (dt) dt AS datetime, co2 AS co2_e FROM (
        SELECT date_trunc('minute',datetime) AS dt, co2
        FROM bor__lic7000_m_v0
         WHERE co2 IS NOT NULL
        AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ORDER BY datetime
    ) AS subq_eddy1
) AS subq_eddy
FULL JOIN (
    SELECT DISTINCT ON (dt) dt AS datetime, ocs, round(co2,1) AS co2_l FROM (
        SELECT date_trunc('minute',datetime) AS dt, ocs,co2
        FROM bor__lgrocs_v0
        WHERE ocs IS NOT NULL
        AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ORDER BY datetime
    ) AS subq_lgr1
) AS subq_lgr
-- PICARRO
FULL JOIN (
    SELECT DISTINCT ON (dt) dt AS datetime, round(co2,1) AS co2_pic, round(ch4,3) AS ch4_pic FROM (
        SELECT date_trunc('minute',datetime) AS dt, co2, ch4
        FROM bor__g2311f_m_v0
        WHERE co2 IS NOT NULL
        AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ORDER BY datetime
    ) AS subq_pic1
) AS subq_picarro
FULL JOIN (
    SELECT generate_series( ( SELECT start_time FROM timerange ), ( SELECT end_time FROM timerange ) - INTERVAL '1 minute', '1 minute') AS datetime
) AS fill
USING (datetime)
USING (datetime)
USING (datetime)
USING (datetime)
ORDER BY datetime ;