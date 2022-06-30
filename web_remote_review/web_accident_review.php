<!doctype html>
<html lang="en">

  <?php
    $url = 'http://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI'];
    $url_components = parse_url($url);
    parse_str($url_components['query'], $params);
    $url_aid = $params['aid'];

    session_start();
    // if dont have session user..then
    if(! isset($_SESSION['userid']))
    {
      session_write_close();
      die("<script>alert('Please login first before proceed!');window.location.href='web_login.html?aid=$url_aid';</script>");
    }
  ?>

  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>e-Vision Remote Review</title>
    <link rel="shortcut icon" href="web_asset/logo.png" type="image/x-icon" />
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-0evHe/X+R7YkIZDRvuzKMRqM+OrBnVFBL6DOitfPri4tjfHxaWutUpFmBp4vmVor" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css?family=Acme&display=swap" rel="stylesheet">

    <style>
      /*style for animated background*/
      .animated-bg{
        min-width: 100%;
        min-height: 100vh;
        background: linear-gradient(-45deg, #EE7752, #E73C7E, #23A6D5, #23D5AB);
        background-size: 400% 400%;
        animation: change 10s ease-in-out infinite;
        padding-top: 40px;
        padding-bottom: 40px;
        font-family: 'Acme', sans-serif;
        color: white;
      }
      @keyframes change{
        0%{
            background-position: 0 50%;
        }
        50%{
            background-position: 100% 50%;
        }
        100%{
            background-position: 0 50%;
        }
      }
      #card {
        /* Add shadows to create the "card" effect */
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        background-color: #343A40;
        width: 85%;
        margin: auto;
        padding: 3%;
        box-shadow: 0 12px 32px 0 lightblue;
      }
      <?php
          $fill = scandir('./web_evidence/');
          $g = 0;
          foreach($fill as $file) {
              if($file !== "." && $file !== ".." && $file !== ".gitignore") {
                echo "#myImg$g {
                        border-radius: 5px;
                        cursor: pointer;
                        transition: 0.3s;
                      }
                
                      #myImg$g:hover {opacity: 0.7;}
                
                      .close$g {
                        position: absolute;
                        top: 15px;
                        right: 35px;
                        color: #f1f1f1;
                        font-size: 40px;
                        font-weight: bold;
                        transition: 0.3s;
                      }
                
                      .close$g:hover,
                      .close$g:focus {
                        color: #bbb;
                        text-decoration: none;
                        cursor: pointer;
                      }";
                $g += 1;
              }
          }
      ?>
      .modal {
        display: none;
        position: fixed;
        z-index: 1;
        padding-top: 100px;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow: auto; 
        background-color: rgb(0,0,0);
        background-color: rgba(0,0,0,0.9);
      }
      .modal-content {
        margin: auto;
        display: block;
        width: 80%;
        max-width: 700px;
      }

      @keyframes zoom {
        from {transform:scale(0)}
        to {transform:scale(1)}
      }

      /* 100% Image Width on Smaller Screens */
      @media only screen and (max-width: 700px){
        .modal-content {
          width: 100%;
        }
      }
    </style>
  </head>

  <body>
    <?php
      include("db_conn.php");//add connection to the php page

      $sql = "SELECT da.acci_id, c.cam_id, c.cam_street, c.cam_city, c.cam_state, da.acci_datetime, da.acci_proof
              FROM DetectedAccident da, Camera c
              WHERE da.cam_id = c.cam_id AND da.acci_id = '".$url_aid."'";
      $result = mysqli_query($conn, $sql);

      while($rows = mysqli_fetch_array($result))
      {
        $aid = $rows['acci_id'];
        $cid = $rows['cam_id'];
        $cstreet = $rows['cam_street'];
        $ccity = $rows['cam_city'];
        $cstate = $rows['cam_state'];
        $adatetime = $rows['acci_datetime'];
        $aproof = $rows['acci_proof'];
      }
      // get evidence
      $output = passthru("python web_get_evidences.py ".$aproof);
    ?>

    <section class="animated-bg">
      <div class="container-fluid" id="card">
        <p class="h2 text-center" style="margin-top: 20px;">Detected Accident Info</p>
        <div class="row">
          <?php
              $files = scandir('./web_evidence/');
              $i = 0;
              foreach($files as $file) {
                  if($file !== "." && $file !== ".." && $file !== ".gitignore") {
                    echo "<div class='col-12 col-sm-6 col-lg-3' style='margin-top: 10px;'>\n
                              <img class='w-100' src='web_evidence/$file' id='myImg$i'>\n
                          </div>\n";
                    $i += 1;
                  }
              }
          ?>
        </div>

        <form action="web_remote_review.php" method="POST" style="margin: 10px 0px 10px 0px;">
          <div class="row">
              <div class="col-xs-6 col-md-6" style="margin: 5px 0px 5px 0px;">
                <div class="input-group flex-nowrap">
                  <span class="input-group-text" id="basic-addon1">Accident ID</span>
                  <input type="text" class="form-control" placeholder="Accident ID" aria-label="acci_id" aria-describedby="basic-addon1" value="<?php echo $aid;?>" name="aid" readonly>
                </div>
              </div>
              <div class="col-xs-6 col-md-6" style="margin: 5px 0px 5px 0px;">
                <div class="input-group flex-nowrap">
                  <span class="input-group-text" id="basic-addon1">Camera ID</span>
                  <input type="text" class="form-control" placeholder="Camera ID" aria-label="cam_id" aria-describedby="basic-addon1" value="<?php echo $cid;?>" readonly>
                </div>
              </div>
          </div>
          <div class="row">
              <div class="col-xs-6 col-md-6" style="margin: 5px 0px 5px 0px;">
                <div class="input-group flex-nowrap">
                  <span class="input-group-text" id="basic-addon1">Location</span>
                  <input type="text" class="form-control" placeholder="Location" aria-label="acci_loc" aria-describedby="basic-addon1" value="<?php echo $ccity . ', ' . $cstate;?>" readonly>
                </div>
              </div>
              <div class="col-xs-6 col-md-6" style="margin: 5px 0px 5px 0px;">
                <div class="input-group flex-nowrap">
                  <span class="input-group-text" id="basic-addon1">Date Time</span>
                  <input type="text" class="form-control" placeholder="Detected Date Time" aria-label="acci_datetime" aria-describedby="basic-addon1" value="<?php echo $adatetime;?>" readonly>
                </div>
              </div>
          </div>
          <input type="text" class="form-control" placeholder="Staff ID" aria-label="acci_datetime" aria-describedby="basic-addon1" value="<?php echo $_SESSION['userid'];?>" name="uid" hidden readonly>
          <div class="d-grid gap-2" style="margin: 10px 0px 20px 0px;">
            <input class="btn btn-warning" type="submit" value="Mark Accident Resolved" name="action" />
            <input class="btn btn-primary" type="submit" value="Mark Non Accident" name="action" />
          </div>
        </form>
      </div>

      <?php
          $fi = scandir('./web_evidence/');
          $h = 0;
          foreach($fi as $file) {
              if($file !== "." && $file !== ".." && $file !== ".gitignore") {
                echo "<div id='myModal$h' class='modal'>\n
                        <span class='close$h'>&times;</span>\n
                        <img class='modal-content' id='img$h'>\n
                      </div>\n";
                $h += 1;
              }
          }
      ?>
    </section>

    <script>
      <?php
          $fil = scandir('./web_evidence/');
          $j = 0;
          foreach($fil as $file) {
              if($file !== "." && $file !== ".." && $file !== ".gitignore") {
                echo "var modal$j = document.getElementById('myModal$j');\n
                  var img$j = document.getElementById('myImg$j');\n
                  var modalImg$j = document.getElementById('img$j');\n
                  img$j.onclick = function(){
                    modal$j.style.display = 'block';\n
                    modalImg$j.src = this.src;\n
                  }\n
                  var span$j = document.getElementsByClassName('close$j')[0];\n

                  span$j.onclick = function() {
                    modal$j.style.display = 'none';\n
                  }\n";
                $j += 1;
              }
          }
      ?>
    </script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.5/dist/umd/popper.min.js" integrity="sha384-Xe+8cL9oJa6tN/veChSP7q+mnSPaj5Bcu9mPX5F5xIGE0DVittaqT5lorf0EI7Vk" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-pprn3073KE6tl6bjs2QrFaJGz5/SUsLqktiwsUTF55Jfv3qYSDhgCecCxMW52nD2" crossorigin="anonymous"></script>
  </body>

</html>