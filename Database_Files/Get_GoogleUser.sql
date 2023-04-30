Delimiter $$
DROP PROCEDURE IF EXISTS Get_GoogleUser$$
CREATE PROCEDURE `Get_GoogleUser` (
    IN user_googleid varchar(255)
)
BEGIN

SELECT user_name,email FROM Users WHERE Google_id =user_googleid;

END$$
Delimiter ;

