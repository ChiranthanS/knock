Delimiter $$
DROP PROCEDURE IF EXISTS Room_History$$
CREATE PROCEDURE `Room_History`(
	room_id VARCHAR(255)
) 
BEGIN

SELECT *
FROM ChatMessages c
WHERE c.room_id = room_id;


END$$
Delimiter ;