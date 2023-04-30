Delimiter $$
DROP PROCEDURE IF EXISTS Get_MobilewithEmail$$
CREATE PROCEDURE `Get_MobilewithEmail` (
    login_email VARCHAR(255)
)
BEGIN
Select U.mobile,SQ.Question,USQ.Security_ans from Users U 
JOIN UserSecurityQuestions USQ on USQ.user_id=U.user_id
JOIN SecurityQuestions SQ on SQ.Question_id=USQ.Question_id
where email=login_email ;
END$$
Delimiter ;