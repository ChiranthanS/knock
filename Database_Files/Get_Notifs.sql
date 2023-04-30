Delimiter $$
DROP PROCEDURE IF EXISTS Get_Notifs$$
CREATE PROCEDURE `Get_Notifs`(
	receiver_id INT
) 
BEGIN

SELECT DISTINCT N.sender_name, N.sender_id, N.receiver_id, N.room_id FROM Notifications N WHERE N.receiver_id=receiver_id;

END$$
Delimiter ;