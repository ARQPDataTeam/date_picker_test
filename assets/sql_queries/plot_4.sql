-- gases plot 2
SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '2024-09-12'::timestamp AS start_time, '2024-09-13'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, co_l, h2o_p, h2o_e, h2o_l, h2o_pic, o3 FROM (
        SELECT DISTINCT ON (dt) dt AS datetime, round(h2o,1) AS h2o_p FROM (
            SELECT date_trunc('minute',datetime) AS dt, h2o
            FROM bor__lic7000_p_v0
            WHERE h2o IS NOT NULL
            AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
            ORDER BY datetime
        ) AS subq_profile1
) AS data2
FULL JOIN (
    SELECT DISTINCT ON (datetime) datetime, round(h2o,1) AS h2o_e 
        FROM bor__lic7000_m_v0
         WHERE h2o IS NOT NULL
            AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ORDER BY datetime
) AS lic7000_data
FULL JOIN (
        SELECT DISTINCT ON (dt) dt AS datetime, round(h2o / 1000,1) AS h2o_l, round(co * 1000,1) AS co_l FROM (
            SELECT date_trunc('minute',datetime) AS dt, h2o,co
            FROM bor__lgrocs_v0
            WHERE h2o IS NOT NULL
            AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
            ORDER BY datetime
        ) AS subq_lgr1
) AS qlgr
FULL JOIN (
        SELECT DISTINCT ON (dt) dt AS datetime, o3 FROM (
            SELECT date_trunc('minute',datetime) AS dt, round(o3_r,1) AS o3
            FROM bor__t49i_v0
             WHERE o3_r IS NOT NULL
             AND o3_r > -10
            AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
            ORDER BY datetime
        ) AS subq_o3_1
) AS t49i_data
FULL JOIN (
    SELECT DISTINCT ON (dt) dt AS datetime, round(h2o * 10 ,2) AS h2o_pic FROM (
            SELECT date_trunc('minute',datetime) AS dt, h2o
            FROM bor__g2311f_m_v0
            WHERE h2o IS NOT NULL
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
USING (datetime)
ORDER BY datetime ;