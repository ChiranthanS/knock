-- Please add all the SP alters in this file

-- Please add all the SP alters in this file

Delimiter $$
DROP PROCEDURE IF EXISTS Create_Order$$
CREATE PROCEDURE `Create_Order` (
    user_id VARCHAR(255),
	sender_name VARCHAR(255), 
    sender_mobile VARCHAR(255), 
    sender_email VARCHAR(255), 
    receiver_name VARCHAR(255), 
    tracking VARCHAR(255), 
    price VARCHAR(255), 
    from_street1 VARCHAR(255), 
    from_street2 VARCHAR(255),
	from_city VARCHAR(255), 
    from_state VARCHAR(255), 
    from_zip VARCHAR(255), 
    to_street1 VARCHAR(255), 
    to_street2 VARCHAR(255),
	to_city VARCHAR(255), 
    to_state VARCHAR(255), 
    to_zip VARCHAR(255),
    service_type VARCHAR(255)

)
BEGIN
INSERT INTO Orders (user_id, sender_name, sender_mobile, sender_email, receiver_name, tracking_id, order_status)
VALUES (CAST(user_id as UNSIGNED),sender_name, sender_mobile, sender_email, receiver_name, tracking,"Order Placed");

Insert INTO OrderDetails (order_id, order_price, from_line1, from_line2, from_city, from_state, from_zip, to_line1, to_line2, to_city, to_state, to_zip, service_type) 
Select max(order_id),price,from_street1,from_street2,from_city,from_state,from_zip,to_street1,to_street2,to_city,to_state,to_zip, service_type from Orders;


END$$
Delimiter ;


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

Delimiter $$
DROP PROCEDURE IF EXISTS Get_Orders$$
CREATE PROCEDURE `Get_Orders`() 
BEGIN

SELECT DISTINCT O.order_id, O.user_id, O.sender_name, O.sender_mobile, O.sender_email, O.receiver_name,
O.tracking_id, O.order_status, O.driver_id, D.order_price, D.from_line1, D.from_line2, D.from_city, D.from_state, D.from_zip,
D.to_line1, D.to_line2, D.to_city, D.to_state, D.to_zip, D.service_type
FROM Orders O
JOIN OrderDetails D ON O.order_id = D.order_id;

END$$
Delimiter ;
