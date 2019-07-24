SELECT *
FROM (
    SELECT *
    FROM event.manual_overides
    WHERE identifier LIKE "CloseOfBusiness%"
    AND cacheIdentifier LIKE "A%"
    AND result LIKE "%TimeAdjustment%"
) AS CloseB -- manual overrides for CloseOfBusiness
INNER JOIN (
    SELECT *
    FROM event.manual_overides
    WHERE identifier LIKE "Audit%"
    AND cacheIdentifier LIKE "A%"
    AND result LIKE "%TimeAdjustment%"
) AS AuditE -- manual overrides for Audit
-- This must be wrong - we won't get any results.
-- Should it be CloseB.cacheIdentifier = AuditE.cacheIdentifier?
ON CloseB.identifier = AuditE.identifier
-- The result was different between 'CloseOfBusiness' and 'Audit'
WHERE CloseB.result <> AuditE.result
