USE banking_website;
CREATE TABLE customer_info (
	SSN CHAR(11) PRIMARY KEY,
    Username VARCHAR(50) NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Address VARCHAR(50) NOT NULL,
    Phone VARCHAR(50) NOT NULL,
    PasswordHash VARCHAR(50) NOT NULL
);

SELECT * FROM customer_info;

ALTER TABLE customer_info
MODIFY approved BOOLEAN NULL DEFAULT NULL;

CREATE TABLE accounts (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    SSN CHAR(11) NOT NULL,
    AccountNumber BIGINT UNIQUE NOT NULL,
    AccountType VARCHAR(20) DEFAULT 'checking',
    Balance DECIMAL(10,2) DEFAULT 0.00,

    FOREIGN KEY (SSN)
        REFERENCES customer_info(SSN)
        ON DELETE CASCADE
);
ALTER TABLE customer_info
MODIFY COLUMN PasswordHash VARCHAR(255) NOT NULL;

ALTER TABLE customer_info
ADD COLUMN approved BOOLEAN NULL;