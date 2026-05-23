<?php

$host = "localhost";
$user = "root";
$pass = "";
$db = "agapay";

$conn = mysqli_connect($host, $user, $pass, $db);

if(!$conn){
    die("Connection Failed");
}

?>