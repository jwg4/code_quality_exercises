SELECT *
FROM event.manual_overides AS CloseB
INNER JOIN 
event.manual_overides AS AuditE
ON CloseB.cacheIdentifier = AuditE.cacheIdentifier
WHERE CloseB.identifier LIKE "CloseOfBusiness%"
AND AuditE.identifier LIKE "Audit%"
AND CloseB.cacheIdentifier LIKE "A%"
AND CloseB.result LIKE "%TimeAdjustment%"
AND AuditE.result LIKE "%TimeAdjustment%"
AND CloseB.result <> AuditE.result
