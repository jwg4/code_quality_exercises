SELECT * FROM(
    SELECT* FROM event.manual_overides WHERE identifier LIKE "CloseOfBusiness%" AND cacheIdentifier LIKE "A%" AND result LIKE "%TimeAdjustment%"
) AS CloseB
INNER JOIN 
(
    SELECT* FROM event.manual_overides WHERE identifier LIKE "Audit%" AND cacheIdentifier LIKE "A%" AND result LIKE "%TimeAdjustment%"
) AS AuditE
ON CloseB.identifier = AuditE.identifier
WHERE CloseB.result <> AuditE.result