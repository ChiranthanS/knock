Delimiter $$
DROP PROCEDURE IF EXISTS Set_status$$
CREATE PROCEDURE `Set_status` (
    tracking varchar(255),
    current_status VARCHAR(255)
)
BEGIN
UPDATE Orders  
SET 
order_status=current_status
WHERE tracking_id=tracking ;

Select order_id from Orders where tracking_id=tracking ;

END$$
Delimiter ;

