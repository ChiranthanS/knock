Delimiter $$
DROP PROCEDURE IF EXISTS Reset_Password$$
CREATE PROCEDURE `Reset_Password` (
    login_email VARCHAR(255),
    H_pass VARCHAR(255)
)
BEGIN

Update UserLogins UL 
JOIN Users U ON U.user_id=UL.user_id
SET UL.user_passkey=H_pass
where U.email=login_email;

END$$
Delimiter ;