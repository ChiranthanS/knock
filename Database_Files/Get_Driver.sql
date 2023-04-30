Delimiter $$
DROP PROCEDURE IF EXISTS Get_Driver$$
CREATE PROCEDURE `Get_Driver`(
    tracking varchar(255)
) 
BEGIN

SELECT driver_id
FROM Orders O
WHERE O.tracking_id = tracking;

END$$
Delimiter ;