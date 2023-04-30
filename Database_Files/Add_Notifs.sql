Delimiter $$
DROP PROCEDURE IF EXISTS Add_Notifs$$
CREATE PROCEDURE `Add_Notifs`(
	sender_name VARCHAR(255),
	sender_id INT,
    receiver_id INT,
	room_id VARCHAR(255)
) 
BEGIN

INSERT INTO Notifications (sender_name, sender_id, receiver_id, room_id) 
VALUES (sender_name, sender_id, receiver_id, room_id);

END$$
Delimiter ;