Delimiter $$
DROP PROCEDURE IF EXISTS Get_status$$
CREATE PROCEDURE `Get_status` (
    tracking varchar(255)
)
BEGIN
SELECT order_status FROM Orders WHERE tracking_id =tracking;
END$$
Delimiter ;

