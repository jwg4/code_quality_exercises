SELECT *
FROM (
    SELECT *
    FROM event.manual_overides
    WHERE identifier LIKE "CloseOfBusiness%"
    AND cacheIdentifier LIKE "A%"
    AND result LIKE "%TimeAdjustment%"
) AS CloseB
INNER JOIN (
    SELECT *
    FROM event.manual_overides
    WHERE identifier LIKE "Audit%"
    AND cacheIdentifier LIKE "A%"
    AND result LIKE "%TimeAdjustment%"
) AS AuditE
-- The intention must be that cacheIdentifier columns match
-- since identifier columns are different by construction.
ON CloseB.cacheIdentifier = AuditE.cacheIdentifier
WHERE CloseB.result <> AuditE.result
