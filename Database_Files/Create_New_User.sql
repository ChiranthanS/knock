
Delimiter $$
DROP PROCEDURE IF EXISTS Create_New_User$$
CREATE PROCEDURE `Create_New_User` (
	user_type_id VARCHAR(255),
    username VARCHAR(255), 
    email VARCHAR(255), 
    H_pass VARCHAR(255), 
    mobile VARCHAR(255), 
    address_line1 VARCHAR(255), 
    city VARCHAR(255), 
    state VARCHAR(255), 
    zip VARCHAR(255),
    Google_id VARCHAR(255),
    security_question VARCHAR(255), 
    security_answer VARCHAR(255)
)
BEGIN

INSERT INTO Users (user_type_id,user_name, email, mobile, address_line1, city, state, zip, Google_id) 
VALUES (CAST(user_type_id as UNSIGNED),username, email,mobile, address_line1, city, state, zip, Google_id);

Insert INTO UserLogins (user_id,user_passkey, is_active) 
Select max(user_id),H_pass,1 from Users;

Insert INTO UserSecurityQuestions (user_id,Question_id,Security_ans,is_active)
Select max(U.user_id),security_question,security_answer,1 from Users U;


END$$
Delimiter ;