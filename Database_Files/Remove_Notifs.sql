Delimiter $$
DROP PROCEDURE IF EXISTS Remove_Notifs$$
CREATE PROCEDURE `Remove_Notifs`(
    receiver_id INT
) 
BEGIN

DELETE FROM Notifications N WHERE N.receiver_id = receiver_id;

END$$
Delimiter ;