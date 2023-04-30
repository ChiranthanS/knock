Delimiter $$
DROP PROCEDURE IF EXISTS Set_location$$
CREATE PROCEDURE `Set_location` (
    trackingid varchar(255),
    street1 VARCHAR(255), 
    street2 VARCHAR(255),
	city VARCHAR(255), 
    state VARCHAR(255), 
    zip VARCHAR(255)
)
BEGIN
UPDATE Orders O 
JOIN OrderDetails OD on O.order_id=OD.order_id
SET 
OD.from_line1 = street1, 
OD.from_line2 = street2, 
OD.from_city = city, 
OD.from_state = state, 
OD.from_zip = zip 
WHERE O.tracking_id= trackingid ;

Select sender_email from Orders where tracking_id=trackingid ;

END$$
Delimiter ;

