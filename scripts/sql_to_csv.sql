WITH RankedResults AS (
    SELECT
        "problem",
        "planner",
        "status",
        "quality",
        "id",
        ROW_NUMBER() OVER (PARTITION BY "problem", "planner" ORDER BY 
            CASE WHEN "status" = 'SOLVED' THEN 0 ELSE 1 END, -- prioritize SOLVED status
            "quality" ASC  -- minimize quality
        ) AS rank
    FROM "results"
    WHERE "planner" IN ('aries', 'aries-optic', 'aries-lpg', 'optic', 'lpg')
)
SELECT
    SUBSTR("problem", INSTR("problem", '-') + 1) AS "instance", -- Remove the 'socs2025-' prefix
    -- Optic columns
    MAX(CASE WHEN "planner" = 'optic' THEN "status" END) AS "optic-status",
    MAX(CASE WHEN "planner" = 'optic' THEN "quality" END) AS "optic-quality",
	
    -- Aries-Optic columns
    MAX(CASE WHEN "planner" = 'aries-optic' THEN "status" END) AS "aries-optic-status",
    MAX(CASE WHEN "planner" = 'aries-optic' THEN "quality" END) AS "aries-optic-quality",
    
    -- LPG columns
    MAX(CASE WHEN "planner" = 'lpg' THEN "status" END) AS "lpg-status",
    MAX(CASE WHEN "planner" = 'lpg' THEN "quality" END) AS "lpg-quality",
	
    -- Aries-LPG columns
    MAX(CASE WHEN "planner" = 'aries-lpg' THEN "status" END) AS "aries-lpg-status",
    MAX(CASE WHEN "planner" = 'aries-lpg' THEN "quality" END) AS "aries-lpg-quality",
	
    -- Aries columns
    MAX(CASE WHEN "planner" = 'aries' THEN "status" END) AS "aries-status",
    MAX(CASE WHEN "planner" = 'aries' THEN "quality" END) AS "aries-quality"
FROM RankedResults
WHERE rank = 1
GROUP BY "problem"
ORDER BY "problem";
