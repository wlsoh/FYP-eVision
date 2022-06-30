<?php

    $aid = $_POST['aid'];
    $uid = $_POST['uid'];
    date_default_timezone_set("Asia/Kuala_Lumpur");
    $dt = date('Y-m-d H:i:s');

    if($_POST["action"] == 'Mark Accident Resolved') {
        $mark = 1;
    }else if($_POST["action"] == 'Mark Non Accident') {
        $mark = 0;
    }

    include("db_conn.php");

    $sql = "SELECT rev_id FROM DetectedAccident WHERE acci_id = '".$aid."'";
    $result = mysqli_query($conn, $sql);
    $row=mysqli_fetch_array($result);

    if(!empty($row['rev_id'])){
        echo '<script>alert("The accident '.$aid.' detected had been review previously!\nYou may close the current window.");</script>';
        echo "<script>window.location.href='web_done.html';</script>";
    }else{
        $sql1 = "INSERT INTO Review (user_id, rev_datetime, rev_isAccident) VALUES ('".$uid."', '".$dt."', ".$mark.")";
        $result4 = mysqli_query($conn, $sql1);
        if(!$result4)
        {
            echo "<script>alert('Error occured! Please contact developer for help!');";
            die("window.close();</script>");
        }else{
            $sql2 = "SELECT * FROM Review WHERE user_id = '".$uid."' and rev_datetime = '".$dt."'";
            $result2 = mysqli_query($conn, $sql2);

            if(mysqli_num_rows($result2)<=0){
                echo "<script>alert('Error occured! Please contact developer for help!');";
                die("window.close();</script>");
            }else{
                $row1=mysqli_fetch_array($result2);
        
                $sql3 = "UPDATE DetectedAccident SET rev_id = '".$row1['rev_id']."' WHERE acci_id = '".$aid."'";
                $result3 = mysqli_query($conn, $sql3);

                if($result3){
                    echo '<script>alert("The accident '.$aid.' detected had been review successfully!\nYou may close the current window.");</script>';
                    session_destroy();
                    echo "<script>window.location.href='web_done.html';</script>";
                }else{
                    echo "<script>alert('Error occured! Please contact developer for help!');";
                    die("window.history.go(-1);</script>");
                }
            }
        }
    }
?>