Delimiter $$
DROP PROCEDURE IF EXISTS Update_Mobile$$
CREATE PROCEDURE `Update_Mobile` (
    userid int,
    mobile int
)
BEGIN

UPDATE Users U 
SET U.mobile = mobile 
WHERE U.user_id = userid;

END$$
Delimiter ;
