Delimiter $$
DROP PROCEDURE IF EXISTS Update_Address$$
CREATE PROCEDURE `Update_Address` (
    userid int,
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255), 
    city VARCHAR(255), 
    state VARCHAR(255), 
    zip VARCHAR(255)
)
BEGIN

UPDATE Users U 
SET U.address_line1 = address_line1, U.address_line2 = address_line2, U.city = city, U.state = state, U.zip = zip
WHERE U.user_id = userid;

END$$
Delimiter ;
