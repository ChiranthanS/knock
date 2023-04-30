Delimiter $$
DROP PROCEDURE IF EXISTS Submit_Review$$
CREATE PROCEDURE `Submit_Review` (
    order_id varchar(255),
    service VARCHAR(255),
    rating VARCHAR(10),
    user_review VARCHAR(255)
)
BEGIN
Insert into UserReviews (order_id,review_comment,rating, service) Values (order_id,user_review,rating, service);
END$$
Delimiter ;

