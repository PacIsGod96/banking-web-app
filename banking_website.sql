USE banking_website;
CREATE TABLE customer_info (
	SSN CHAR(11) PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Address VARCHAR(50) NOT NULL,
    Phone VARCHAR(50) NOT NULL,
    PasswordHash VARCHAR(50) NOT NULL
)