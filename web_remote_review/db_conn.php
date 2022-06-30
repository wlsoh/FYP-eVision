<?php
    define('DB_SERVER', 'mydatabase.cdkg8rguncrh.ap-southeast-1.rds.amazonaws.com');
    define('DB_USERNAME', 'admin');
    define('DB_PASSWORD', '%Abc040231');
    define('DB_DATABASE', 'eVision');

    /* Connect to MySQL and select the database. */
    $conn = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DATABASE);

    if (mysqli_connect_errno()) echo "Failed to connect to MySQL: " . mysqli_connect_error();

?>