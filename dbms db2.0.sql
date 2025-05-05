SHOW DATABASES;
DROP DATABASE PeakhotelDb;
CREATE DATABASE PeakHotelDb;
Show tables from PeakHotelDb
SHOW TRIGGERS;
SHOW FULL TABLES WHERE Table_type = 'VIEW';

SET SQL_SAFE_UPDATES = 0;
SET SQL_SAFE_UPDATES = 1;  
SET FOREIGN_KEY_CHECKS = 0;
SET FOREIGN_KEY_CHECKS = 1;
USE PeakhotelDb

CREATE TABLE Guest (
GuestID INT PRIMARY KEY AUTO_INCREMENT,
Name VARCHAR(50) NOT NULL,
DOB DATE NOT NULL,
Gender VARCHAR(10) DEFAULT 'Other' CHECK (Gender IN ('Male', 'Female', 'Other')),
AadharNo CHAR(12) NOT NULL UNIQUE CHECK (AadharNo REGEXP '^[0-9]{12}$'),
AddrID INT, 
FOREIGN KEY (AddrID) REFERENCES Address(AddrID) ON DELETE CASCADE
);

CREATE TABLE GuestMobile (
    GuestID INT,
    MobNo CHAR(10) NOT NULL CHECK (MobNo REGEXP '^[0-9]{10}$'),
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE
);

CREATE TABLE Address (
    AddrID INT PRIMARY KEY AUTO_INCREMENT,  
    Street VARCHAR(100) NOT NULL,  
    Village VARCHAR(100) NOT NULL,  
    District VARCHAR(100) NOT NULL,  
    State VARCHAR(100) NOT NULL,  
    PinCode CHAR(6) NOT NULL CHECK (PinCode REGEXP '^[0-9]{6}$')  
);

CREATE TABLE Employee (
    EmployeeID INT PRIMARY KEY AUTO_INCREMENT,  
    Name VARCHAR(100) NOT NULL,  
    DOB DATE NOT NULL,  
    Gender VARCHAR(10) CHECK (Gender IN ('Male', 'Female', 'Other')),  
    Email VARCHAR(100) NOT NULL UNIQUE CHECK (Email REGEXP '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),   
    AddrID INT NOT NULL,    
    PositionTitle VARCHAR(100) NOT NULL,  
    FOREIGN KEY (AddrID) REFERENCES Address(AddrID) ON DELETE CASCADE  
    FOREIGN KEY (PositionTitle) REFERENCES PositionDetails(PositionTitle) ON DELETE CASCADE;
);

CREATE TABLE PositionDetails (
    PositionTitle VARCHAR(50) PRIMARY KEY,
    Salary DECIMAL(10,2) NOT NULL CHECK (Salary > 0)
);
select * from PositionDetails;

CREATE TABLE EmployeeMobile (
    EmployeeID INT,
    MobileNumber CHAR(10) NOT NULL CHECK (MobileNumber REGEXP '^[0-9]{10}$'),
    FOREIGN KEY (EmployeeID) REFERENCES Employee(EmployeeID) ON DELETE CASCADE
);

CREATE TABLE Room (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,  
    RoomNumber VARCHAR(10) NOT NULL UNIQUE,  
    RoomType VARCHAR(50) NOT NULL,  
    Availability BOOLEAN NOT NULL DEFAULT TRUE
    FOREIGN KEY (RoomType) REFERENCES RoomTypeDetails(RoomType);
);

CREATE TABLE RoomTypeDetails (
    RoomType VARCHAR(50) PRIMARY KEY,
    PricePerNight DECIMAL(10,2) NOT NULL CHECK (PricePerNight > 100)
);

CREATE TABLE Reservation (
    ReservationID INT PRIMARY KEY AUTO_INCREMENT,  
    GuestID INT NOT NULL,  
    RoomID INT NOT NULL,  
    CheckInDate DATE NOT NULL,  
    CheckOutDate DATE NOT NULL,  
    TotalNights INT GENERATED ALWAYS AS (DATEDIFF(CheckOutDate, CheckInDate)) STORED,  
    TotalPrice DECIMAL(10,2) NOT NULL,  
    PaymentStatus BOOLEAN NOT NULL DEFAULT FALSE
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID) ON DELETE CASCADE
);

CREATE TABLE Payment (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,  
    GuestID INT NOT NULL,  
    TransactionID VARCHAR(50) NOT NULL,  
    PaymentMethod VARCHAR(50) NOT NULL CHECK (PaymentMethod IN ('Cash', 'Credit Card', 'Debit Card', 'Online')),  
    PaymentDate DATE NOT NULL,  
    Amount DECIMAL(10,2) NOT NULL CHECK (Amount > 0),  
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE
    );

    CREATE TABLE Parking (
    ParkingID INT PRIMARY KEY AUTO_INCREMENT,  
    GuestID INT NOT NULL,  
    VehicleNum VARCHAR(20) NOT NULL CHECK (VehicleNum REGEXP '^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'),  
    ParkingFee DECIMAL(10,2) NOT NULL CHECK (ParkingFee >= 0), 
    PaymentStatus BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE
);

CREATE TABLE Feedback (
    GuestID INT NOT NULL,  
    Rating INT NOT NULL CHECK (Rating BETWEEN 1 AND 5),  
    ServiceType VARCHAR(100) NOT NULL,  
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE
);

CREATE TABLE Restaurant (
    RestaurantID INT PRIMARY KEY AUTO_INCREMENT,  
    Name VARCHAR(100) NOT NULL UNIQUE,  
    SeatingCapacity INT NOT NULL CHECK (SeatingCapacity > 0),  
);
  
  CREATE TABLE RestaurantMobile (
    RestaurantID INT,
    MobileNumber CHAR(10) NOT NULL CHECK (MobileNumber REGEXP '^[0-9]{10}$'),
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
);

CREATE TABLE Menu (
    MenuID INT PRIMARY KEY AUTO_INCREMENT,  
    RestaurantID INT NOT NULL,  
    ItemName VARCHAR(100) NOT NULL,  
    Price DECIMAL(10,2) NOT NULL CHECK (Price > 0),  
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
);

CREATE TABLE OrderTable (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,  
    GuestID INT NOT NULL,  
    RestaurantID INT NOT NULL,  
    OrderDate DATE NOT NULL,  
    TotalAmount DECIMAL(10,2) NOT NULL CHECK (TotalAmount >= 0),  
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE,  
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE,
    PaymentStatus BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE EventHall (
    HallID INT PRIMARY KEY AUTO_INCREMENT,  
    Name VARCHAR(100) NOT NULL UNIQUE,  
    Capacity INT NOT NULL CHECK (Capacity > 0),  
    PricePerHour DECIMAL(10,2) NOT NULL CHECK (PricePerHour > 0),
    Availability BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE EventBooking (
    BookingID INT PRIMARY KEY AUTO_INCREMENT,  
    GuestID INT NOT NULL,  
    HallID INT NOT NULL,  
    EventType VARCHAR(100) NOT NULL,  
    TotalCost DECIMAL(10,2) NOT NULL CHECK (TotalCost >= 0),  
    FOREIGN KEY (GuestID) REFERENCES Guest(GuestID) ON DELETE CASCADE,  
    FOREIGN KEY (HallID) REFERENCES EventHall(HallID) ON DELETE CASCADE,
    PaymentStatus BOOLEAN NOT NULL DEFAULT FALSE
); 

CREATE TABLE Driver (
    DriverID INT PRIMARY KEY AUTO_INCREMENT,  
    Name VARCHAR(50) NOT NULL,  
    Age TINYINT NOT NULL CHECK (Age BETWEEN 18 AND 99),   
    Gender VARCHAR(10) NOT NULL CHECK (Gender IN ('Male', 'Female', 'Other')),  
    CarName VARCHAR(50) NOT NULL,  
    CarNumber VARCHAR(15) NOT NULL UNIQUE CHECK (CarNumber REGEXP '^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$'), 
    Location VARCHAR(50) NOT NULL,  
    MobNumber VARCHAR(15) NOT NULL CHECK (MobNumber REGEXP '^[0-9]{10}$') 
);

CREATE TABLE hotel (
    hotelid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    hotel_phone VARCHAR(15) NOT NULL CHECK (hotel_phone REGEXP '^[0-9]{10,15}$'), 
    owner_name VARCHAR(100) NOT NULL, 
    owner_mobile VARCHAR(15) NOT NULL CHECK (owner_mobile REGEXP '^[0-9]{10,15}$'), 
    owner_email VARCHAR(100) NOT NULL UNIQUE CHECK (owner_email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'), 
    owner_dob DATE NOT NULL 
);
