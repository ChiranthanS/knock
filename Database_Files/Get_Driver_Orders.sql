Delimiter $$
DROP PROCEDURE IF EXISTS Get_Driver_Orders$$
CREATE PROCEDURE `Get_Driver_Orders`(
    driverid int
) 
BEGIN

SELECT DISTINCT O.order_id, O.user_id, O.sender_name, O.sender_mobile, O.sender_email, O.receiver_name,
O.tracking_id, O.order_status, O.driver_id, D.order_price, D.from_line1, D.from_line2, D.from_city, D.from_state, D.from_zip,
D.to_line1, D.to_line2, D.to_city, D.to_state, D.to_zip
FROM Orders O
JOIN OrderDetails D ON O.order_id = D.order_id
WHERE O.driver_id = driverid;

END$$
Delimiter ;