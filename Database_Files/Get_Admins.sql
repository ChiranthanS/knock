Delimiter $$
DROP PROCEDURE IF EXISTS Get_Admins$$
CREATE PROCEDURE `Get_Admins`() 
BEGIN

SELECT *
FROM Users
WHERE user_type_id = 1;


END$$
Delimiter ;