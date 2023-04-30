Delimiter $$
DROP PROCEDURE IF EXISTS Assign$$
CREATE PROCEDURE `Assign` (
    orderid int,
    driverid int
)
BEGIN

UPDATE Orders O
SET O.driver_id = driverid, O.order_status = "In Transit"
WHERE O.order_id = orderid;

END$$
Delimiter ;