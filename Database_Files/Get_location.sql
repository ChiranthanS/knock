Delimiter $$
DROP PROCEDURE IF EXISTS Get_location$$
CREATE PROCEDURE `Get_location` (
    tracking varchar(255)
)
BEGIN

Select 
OD.from_line1,
OD.from_line2,
OD.from_city,
OD.from_state,
OD.from_zip 
from Orders O 
JOIN OrderDetails OD on O.order_id=OD.order_id
WHERE O.tracking_id=tracking;


END$$
Delimiter ;

