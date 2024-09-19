-- Rad
SET TIMEZONE TO 'GMT';
WITH timerange AS ( SELECT '2024-09-12'::timestamp AS start_time, '2024-09-13'::timestamp AS end_time )
SELECT datetime AT TIME ZONE 'GMT' AS datetime, par_in, par_refl, par_line, sw_in, sw_out, lw_in, lw_out, par * 323.7 - 1.26 FROM (
    SELECT DISTINCT ON (dt) dt AS datetime, par_in, par_refl, par_line, sw_in, sw_out, lw_in, lw_out FROM (
    	SELECT date_trunc('minute',datetime) AS dt, *
	    FROM bor__cr23x_m_v0
		WHERE par_in IS NOT NULL 
	    AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
    ) AS ranked
) AS met
FULL JOIN ( 
	SELECT DISTINCT ON (dt) dt AS datetime, par FROM (
	    SELECT date_trunc('minute',datetime) AS dt, par
	    FROM bor__par_v0
	    WHERE par IS NOT NULL
	    AND datetime >= ( SELECT start_time FROM timerange ) AND datetime < ( SELECT end_time FROM timerange )
	    AND par IS NOT NULL
	    ORDER BY datetime
    ) AS subq_par
) AS subq_par_reduced
FULL JOIN (
	SELECT generate_series( ( SELECT start_time FROM timerange ), ( SELECT end_time FROM timerange ) - INTERVAL '1 minute', '1 minute') AS datetime            
) AS fill
USING (datetime)
USING (datetime)
ORDER BY datetime ;

