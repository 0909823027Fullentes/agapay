<?php
include "connect.php";

if(isset($_POST['login'])){

    $username = $_POST['username'];
    $password = $_POST['password'];

    $sql = "SELECT * FROM admins 
            WHERE username='$username' 
            AND password='$password'";

    $result = mysqli_query($conn, $sql);  

    if(mysqli_num_rows($result) > 0){
        header("Location: dashboard.php");
        exit();
    } 
    else {
        echo "<script>alert('Invalid Admin');</script>";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="admin.css">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Admin Login</title>
  <link rel="stylesheet" href="admin.css">
</head>
<body>

  <div class="container">
    <h1>Admin Login</h1>

    <form method="POST">

      <input type="text" name="username" placeholder="Username" required><br>

      <input type="password" name="password" placeholder="Password" required>

      <div class="info">
        User: Admin <br>
        Password: Admin
      </div>

      <button type="submit" name="login" class="btn">
        <a href="dashboard.php">Login</a>
      </button>

    </form>

  </div>

</body>
</html>