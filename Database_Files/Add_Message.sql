Delimiter $$
DROP PROCEDURE IF EXISTS Add_Message$$
CREATE PROCEDURE `Add_Message`(
	user_name VARCHAR(255),
	room_id VARCHAR(255),
    message VARCHAR(255),
	date_time VARCHAR(255)
) 
BEGIN

INSERT INTO ChatMessages (user_name, room_id, message, date_time) 
VALUES (user_name, room_id, message, date_time);

END$$
Delimiter ;