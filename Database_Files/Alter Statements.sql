ALTER TABLE Users MODIFY address_line1 varchar(255);
ALTER TABLE Users MODIFY city varchar(255);
ALTER TABLE Users MODIFY state varchar(255);
ALTER TABLE Users MODIFY zip varchar(255);
ALTER TABLE Users MODIFY mobile varchar(255);

ALTER TABLE Users ADD Google_id varchar(255);

ALTER TABLE Orders ADD driver_id int;

ALTER TABLE OrderDetails ADD service_type varchar(255);

ALTER TABLE UserReviews ADD service VARCHAR(255);

ALTER TABLE Users ADD security_question varchar(255);

ALTER TABLE Users ADD security_answer varchar(255);

ALTER TABLE UserSecurityQuestions MODIFY Question_id INT;
ALTER TABLE UserSecurityQuestions MODIFY Security_ans VARCHAR(255) ;
SET FOREIGN_KEY_CHECKS = 0;
ALTER TABLE SecurityQuestions MODIFY Question_id INT ;
SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO SecurityQuestions (Question_id,Question) Values (0,'Google User');

ALTER TABLE ChatMessages ADD date_time VARCHAR(255);
