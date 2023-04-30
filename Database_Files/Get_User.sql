Delimiter $$
DROP PROCEDURE IF EXISTS Get_User$$
CREATE PROCEDURE `Get_User` (
    IN userid int
)
BEGIN

Select U.user_name, U.email, U.user_type_id, U.Google_id, UL.user_passkey,SQ.Question,USQ.Security_ans
from Users U 
JOIN UserLogins UL on U.user_id = UL.user_id
JOIN UserSecurityQuestions USQ on USQ.user_id=U.user_id
JOIN SecurityQuestions SQ on SQ.Question_id=USQ.Question_id
WHERE U.user_id=userid;


END$$
Delimiter ;
