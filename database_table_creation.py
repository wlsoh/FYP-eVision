# Developer Name: Soh Wee Liam
# Intake: UC3F2111CS(IS)
# Program Name: To initialize the database schema and table creation in the AWS RDS
# Date Created: 29/04/2022
from pickle import FALSE, TRUE
import pymysql
from pymysql.constants import CLIENT

# Create connection to the AWS RDS Free Tier created
db = pymysql.connect(
    host='mydatabase.cdkg8rguncrh.ap-southeast-1.rds.amazonaws.com',
    user='admin',
    password='%Abc040231',
    client_flag=CLIENT.MULTI_STATEMENTS
)
if(db):
    print("Connection Successful")
else:
    print("Connetion Unsucessful")
cursor = db.cursor()

# Check if database schema existed
exist = FALSE
cursor.execute('Show databases')
for db in cursor:
  if(db[0] == 'eVision'):
    print("Database Existed!\n")
    exist = TRUE
    break
  else:
    print("Database Not Exist!\n")

if(exist == FALSE):
  # If database was not found, create the database & table
  # Create and use the database schema
  sql = '''CREATE DATABASE eVision'''
  cursor.execute(sql)
  cursor.connection.commit()
  cursor.execute('USE eVision')
  
  # Create User table and insert a default admin
  sql = '''
  CREATE TABLE User_seq
  (
    user_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
  );
  CREATE TABLE User (
      user_id CHAR(5) NOT NULL DEFAULT '0',
      user_firstname VARCHAR(30) NOT NULL,
      user_lastname VARCHAR(30) NOT NULL,
      user_password VARCHAR(128) NOT NULL,
      user_addressline VARCHAR(255) NOT NULL,
      user_city VARCHAR(30) NOT NULL,
      user_state VARCHAR(30) NOT NULL,
      user_postcode VARCHAR(5) NOT NULL,
      user_email VARCHAR(255) NOT NULL,
      user_phone VARCHAR(15) NOT NULL,
      user_role TINYINT(1) NOT NULL DEFAULT '2',
      user_avatar VARCHAR(255) NOT NULL DEFAULT '1cqBLIEBhkWQ1qmRSi1UehZ7pYKeGQm8e',
      user_lastlogin_datetime DATETIME NULL,
      user_firstLogin TINYINT(1) NOT NULL DEFAULT '1',
      user_isDelete TINYINT(1) NOT NULL DEFAULT '0',
      PRIMARY KEY (user_id)
      );
  CREATE TRIGGER tg_User_insert
  BEFORE INSERT ON User
  FOR EACH ROW
  BEGIN
    INSERT INTO User_seq VALUES (NULL);
    SET NEW.user_id = CONCAT('U', LPAD(LAST_INSERT_ID(), 4, '0'));
  END;
  INSERT INTO User (user_firstname, user_lastname, user_password, user_addressline, user_city, user_state, user_postcode, user_email, user_phone, user_role, user_firstLogin)
  SELECT * FROM (SELECT 'Admin', 'Default', 'admin1010', 'Level 20, Axiata Tower, Jalan Stesen Sentral 5', 'Kuala Lumpur Sentral', 'Kuala Lumpur', '50470', 'evisionmalaysia@gmail.com', '012-3456789', 1, 0) AS tmp
  WHERE NOT EXISTS (
      SELECT user_firstname FROM User WHERE user_firstname = 'Admin'
  ) LIMIT 1;
  '''
  cursor.execute(sql)


  # Create Camera table
  sql = '''
  CREATE TABLE Camera_seq
  (
    cam_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
  );
  CREATE TABLE Camera (
      cam_id CHAR(5) NOT NULL DEFAULT '0',
      cam_desc VARCHAR(255) NULL,
      cam_type VARCHAR(30) NOT NULL,
      cam_source VARCHAR(255) NOT NULL,
      cam_street VARCHAR(255) NOT NULL,
      cam_city VARCHAR(30) NOT NULL,
      cam_state VARCHAR(30) NOT NULL,
      cam_latitude DECIMAL(10,8) NOT NULL,
      cam_longitude DECIMAL(11,8) NOT NULL,
      cam_isDelete TINYINT(1) NOT NULL DEFAULT '0',
      PRIMARY KEY (cam_id)
      );
  CREATE TRIGGER tg_Camera_insert
  BEFORE INSERT ON Camera
  FOR EACH ROW
  BEGIN
    INSERT INTO Camera_seq VALUES (NULL);
    SET NEW.cam_id = CONCAT('C', LPAD(LAST_INSERT_ID(), 4, '0'));
  END;
  '''
  cursor.execute(sql)
  
  # Create User_Camera table
  sql = '''
  CREATE TABLE User_Camera (
      user_id CHAR(5) NOT NULL,
      cam_id CHAR(5) NOT NULL,
      FOREIGN KEY (user_id) REFERENCES User(user_id),
      FOREIGN KEY (cam_id) REFERENCES Camera(cam_id)
    );
  '''
  cursor.execute(sql)
  
  # Create Review table
  sql = '''
  CREATE TABLE Review_seq
  (
    rev_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
  );
  CREATE TABLE Review (
      rev_id CHAR(5) NOT NULL DEFAULT '0',
      user_id CHAR(5) NOT NULL,
      rev_datetime DATETIME NOT NULL,
      rev_isAccident TINYINT(1) NOT NULL,
      PRIMARY KEY (rev_id),
      FOREIGN KEY (user_id) REFERENCES User(user_id)
  );  
  CREATE TRIGGER tg_Review_insert
  BEFORE INSERT ON Review
  FOR EACH ROW
  BEGIN
    INSERT INTO Review_seq VALUES (NULL);
    SET NEW.rev_id = CONCAT('R', LPAD(LAST_INSERT_ID(), 4, '0'));
  END;
  '''
  cursor.execute(sql)
  
  # create AccidentDetected table
  sql = '''
  CREATE TABLE DetectedAccident_seq
  (
    acci_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY
  );
  CREATE TABLE DetectedAccident (
      acci_id CHAR(5) NOT NULL DEFAULT '0',
      cam_id CHAR(5) NOT NULL,
      rev_id CHAR(5) NOT NULL,
      acci_datetime DATETIME NOT NULL,
      acci_proof VARCHAR(255) NOT NULL,
      PRIMARY KEY (acci_id),
      FOREIGN KEY (cam_id) REFERENCES Camera(cam_id),
      FOREIGN KEY (rev_id) REFERENCES Review(rev_id)
  );  
  CREATE TRIGGER tg_DetectedAccident_insert
  BEFORE INSERT ON DetectedAccident
  FOR EACH ROW
  BEGIN
    INSERT INTO DetectedAccident_seq VALUES (NULL);
    SET NEW.acci_id = CONCAT('A', LPAD(LAST_INSERT_ID(), 4, '0'));
  END;
  '''
  cursor.execute(sql)
  print("The eVision database schema created successfully!")
else:
  print("The database schema already existed!")


