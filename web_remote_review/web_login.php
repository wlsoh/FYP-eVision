<?php

    session_start();

    include("db_conn.php");

    $email = mysqli_real_escape_string($conn,$_POST['email']);
    $email = strtolower($email);
    $password = mysqli_real_escape_string($conn,$_POST['password']);
    $params = $_POST['params'];

    $sql = "SELECT * FROM User WHERE user_email = '".$email."' AND BINARY user_password = SHA2('".$password."', 256)";
    $result = mysqli_query($conn, $sql);

    if(mysqli_num_rows($result)<=0){
        echo "<script>alert('Invalid username/password! Please Try Again!');";
        die("window.history.go(-1);</script>");
    }else{
        $row=mysqli_fetch_array($result);

        if ($row['user_isDelete'] == 1){
            echo '<script>alert("Your e-Vision account had been deactivated! Please contact company Admin for assistance.")</script>';
            die("<script>window.history.go(-1);</script>");
        }else{
            $_SESSION['userid'] = $row['user_id'];

            echo "<script>window.location.href='web_accident_review.php?aid=$params';</script>";
        }
    }

?>