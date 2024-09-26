-- status plot 1 - amb temps 1

SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '{}'::timestamp AS start_time, '{}'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, temp1m,temp3m,temp6m,temp10m,temp13m,temp16m,temp19m,temp22m,temp25m,temp29m,temp33m,temp42m FROM (
    SELECT DISTINCT ON (datetime) * FROM (
        SELECT date_trunc('minute',datetime) AS datetime, temp1m,temp3m,temp6m,temp10m,temp13m,temp16m,temp19m,temp22m,temp25m,temp29m,temp33m,temp42m
        FROM bor__cr3000_v0
        WHERE temp1m IS NOT NULL
        AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
    ) AS sub
) AS data
FULL JOIN (
    SELECT generate_series( ( SELECT start_time FROM timerange ), ( SELECT end_time FROM timerange ) - INTERVAL '1 minute', '1 minute') AS datetime
) AS fill
USING (datetime)
ORDER BY datetime ; 

-- plot 2

SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '{}'::timestamp AS start_time, '{}'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, vtempa, temp33m, temp42m FROM (
    SELECT DISTINCT ON (datetime) * FROM (
        SELECT date_trunc('minute',datetime) AS datetime, temp33m, tempa AS temp42m
        FROM bor__cr23x_m_v0
         WHERE temp33m IS NOT NULL
         AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
    ) AS sub
) AS met
FULL JOIN (
    SELECT DISTINCT ON (datetime) * FROM (
        SELECT date_trunc('minute',datetime) AS datetime, round(vtempa,1) AS vtempa
	    FROM bor__csat_m_v0 
	    WHERE vtempa IS NOT NULL
	     AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
    ) AS subq_csat
) AS csat
FULL JOIN (
    SELECT generate_series( ( SELECT start_time FROM timerange ), ( SELECT end_time FROM timerange ) - INTERVAL '1 minute', '1 minute') AS datetime
) AS fill
USING (datetime)
USING (datetime)
ORDER BY datetime ; 