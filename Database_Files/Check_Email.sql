Delimiter $$
DROP PROCEDURE IF EXISTS Check_Email$$
CREATE PROCEDURE `Check_Email` (
    email varchar(255)
)
BEGIN

 SELECT U.user_id,user_name,U.user_type_id,U.Google_id, UL.user_passkey,SQ.Question,USQ.Security_ans
 FROM Users U 
 JOIN UserLogins UL on U.user_id=UL.user_id
 JOIN UserSecurityQuestions USQ on U.user_id=USQ.user_id
 JOIN SecurityQuestions SQ on SQ.Question_id=USQ.Question_id
 WHERE U.email =email and UL.is_active=1 and USQ.is_active=1;

END$$
Delimiter ;