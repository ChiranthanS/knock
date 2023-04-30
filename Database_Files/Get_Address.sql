Delimiter $$
DROP PROCEDURE IF EXISTS Get_Address$$
CREATE PROCEDURE `Get_Address` (
    IN userid int
)
BEGIN

Select * from Users U 
WHERE U.user_id=userid;

END$$
Delimiter ;