-- Create Database
CREATE DATABASE IF NOT EXISTS train_reservation;
USE train_reservation;

-- ===========================
--  TABLE: trains
-- ===========================
CREATE TABLE IF NOT EXISTS trains (
    train_id INT PRIMARY KEY AUTO_INCREMENT,
    train_number VARCHAR(20) NOT NULL,
    train_name VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    total_seats INT NOT NULL
);

-- ===========================
--  TABLE: schedules
-- ===========================
CREATE TABLE IF NOT EXISTS schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    train_id INT NOT NULL,
    travel_date DATE NOT NULL,
    departure_time VARCHAR(10) NOT NULL,
    arrival_time VARCHAR(10) NOT NULL,
    fare DECIMAL(10,2) NOT NULL,
    available_seats INT NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(train_id)
);

-- ===========================
--  TABLE: passengers
-- ===========================
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100)
);

-- ===========================
--  TABLE: bookings
-- ===========================
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT NOT NULL,
    passenger_id INT NOT NULL,
    seats_booked INT NOT NULL,
    booking_time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
);

-- ===========================
--  SAMPLE DATA (Optional)
--  Delete this section if you want an empty DB
-- ===========================

INSERT INTO trains (train_number, train_name, source, destination, total_seats) VALUES
('12601', 'Chennai Express', 'Chennai', 'Bangalore', 200),
('12710', 'Hyderabad Superfast', 'Chennai', 'Hyderabad', 180),
('12850', 'Night Express', 'Bangalore', 'Hyderabad', 220);

INSERT INTO schedules (train_id, travel_date, departure_time, arrival_time, fare, available_seats) VALUES
(1, '2025-12-05', '06:00', '11:30', 550.00, 200),
(1, '2025-12-06', '16:00', '21:30', 600.00, 200),
(2, '2025-12-05', '08:00', '15:00', 750.00, 180),
(3, '2025-12-05', '22:30', '06:30', 900.00, 220);