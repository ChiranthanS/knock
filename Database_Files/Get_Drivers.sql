Delimiter $$
DROP PROCEDURE IF EXISTS Get_Drivers$$
CREATE PROCEDURE `Get_Drivers`() 
BEGIN

SELECT *
FROM Users
WHERE user_type_id = 2;


END$$
Delimiter ;