Delimiter $$
DROP PROCEDURE IF EXISTS Create_New_GoogleUser$$
CREATE PROCEDURE `Create_New_GoogleUser` (
    username VARCHAR(255), 
    email VARCHAR(255), 
    Google_id VARCHAR(255)
)
BEGIN
INSERT INTO Users (user_name, email, Google_id) VALUES (username, email, Google_id);
END$$
Delimiter ;

