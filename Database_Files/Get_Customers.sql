Delimiter $$
DROP PROCEDURE IF EXISTS Get_Customers$$
CREATE PROCEDURE `Get_Customers`() 
BEGIN

SELECT *
FROM Users
WHERE user_type_id = 3;


END$$
Delimiter ;