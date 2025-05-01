-- Create the database
CREATE DATABASE IF NOT EXISTS hospitaldb;
USE hospitaldb;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100) NOT NULL
);

-- Patient table
CREATE TABLE IF NOT EXISTS patient (
    P_ID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Age INT,
    Gender VARCHAR(10),
    DOB DATE
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    A_ID INT AUTO_INCREMENT PRIMARY KEY,
    P_ID INT NOT NULL,
    Doctor_Name VARCHAR(100),
    Appointment_Date DATE,
    Appointment_Time TIME,
    Reason TEXT,
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    B_ID INT AUTO_INCREMENT PRIMARY KEY,
    P_ID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Bill_Date DATE NOT NULL,
    FOREIGN KEY (P_ID) REFERENCES patient(P_ID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Stored Procedure to insert bill data
DELIMITER //

CREATE PROCEDURE AddBill(
    IN b_id INT,
    IN p_id INT,
    IN amt DECIMAL(10,2),
    IN bill_dt DATE
)
BEGIN
    INSERT INTO bills (B_ID, P_ID, Amount, Bill_Date)
    VALUES (b_id, p_id, amt, bill_dt);
END;
//

DELIMITER ;

-- Insert default admin user
INSERT INTO users (username, password)
VALUES ('admin', 'admin');
