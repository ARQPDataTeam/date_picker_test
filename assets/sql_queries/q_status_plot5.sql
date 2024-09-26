-- ozone
SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '2024-09-12'::timestamp AS start_time, '2024-09-13'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, o3_i , o3_b, no, o3_pmt FROM (
	SELECT DISTINCT ON (dt) dt AS datetime, o3 AS o3_b FROM (
	   SELECT date_trunc('minute',datetime) AS dt, o3
            FROM bor__o32b_v0
             WHERE o3 IS NOT NULL
             AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
            ORDER BY datetime
 		) subq_2b
	) AS subq_2b_reduced
FULL JOIN (
    SELECT date_trunc('minute',datetime) AS datetime, no
        FROM bor__t42i_l_v0
         WHERE no IS NOT NULL
        --AND substr(status, 3, 1) = '1'
         AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ) AS data_42i_lrec
FULL JOIN (
        SELECT datetime, pmt AS o3_pmt 
            FROM bor__pmt_m_v0
             WHERE pmt IS NOT NULL
             AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
        ) AS subq_pmt
FULL JOIN (
        SELECT DISTINCT ON (dt) dt AS datetime, o3_r AS o3_i FROM (
            SELECT date_trunc('minute',datetime) AS dt, o3_r
	            FROM bor__t49i_v0
	             WHERE o3_r IS NOT NULL
		         AND o3_r > -10
	             AND substr(status, 3, 1) = '1'
	             AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
	            ORDER BY datetime
	        ) AS subq_49i
        ) AS subq_49i_reduced
FULL JOIN (
       SELECT generate_series( ( SELECT start_time FROM timerange ), ( SELECT end_time FROM timerange ) - INTERVAL '1 minute', '1 minute') AS datetime     
) AS fill
USING (datetime)
USING (datetime)
USING (datetime)
USING (datetime)
ORDER BY datetime ; 

