Delimiter $$
DROP PROCEDURE IF EXISTS Get_Reviews$$
CREATE PROCEDURE `Get_Reviews`()

BEGIN
SELECT UR.*,U.user_name FROM UserReviews UR 
JOIN Orders O on UR.order_id=O.order_id
JOIN Users U on U.user_id=O.user_id;

END$$
Delimiter ;
