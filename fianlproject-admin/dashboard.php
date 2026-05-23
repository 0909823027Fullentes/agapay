<?php

$conn = new mysqli(
    "localhost",
    "root",
    "",
    "agapay"
);

if ($conn->connect_error) {
    die("Connection Failed: " . $conn->connect_error);
}

// ==========================================
// APPROVE USER
// ==========================================
if(isset($_POST['approve'])){

    $id = $_POST['id'];

    $schedule_date = $_POST['schedule_date'];
    $schedule_time = $_POST['schedule_time'];

    $sql = "
        UPDATE users
        SET
            status='Approved',
            schedule_date='$schedule_date',
            schedule_time='$schedule_time'
        WHERE id='$id'
    ";

    $conn->query($sql);

    $message = "
Your request has been APPROVED

Schedule Date:
$schedule_date

Schedule Time:
$schedule_time
";

    $notif = "
        INSERT INTO notifications
        (
            user_id,
            message
        )
        VALUES
        (
            '$id',
            '$message'
        )
    ";

    $conn->query($notif);

    header("Location: dashboard.php");
    exit();
}

// ==========================================
// REJECT USER
// ==========================================
if(isset($_POST['reject'])){

    $id = $_POST['id'];

    $sql = "
        UPDATE users
        SET status='Rejected'
        WHERE id='$id'
    ";

    $conn->query($sql);

    $message = "
Your request has been REJECTED.
Please contact the administrator.
";

    $notif = "
        INSERT INTO notifications
        (
            user_id,
            message
        )
        VALUES
        (
            '$id',
            '$message'
        )
    ";

    $conn->query($notif);

    header("Location: dashboard.php");
    exit();
}

// ==========================================
// BAN USER
// ==========================================
if(isset($_POST['ban'])){

    $id = $_POST['id'];

    $sql = "
        UPDATE users
        SET status='Banned'
        WHERE id='$id'
    ";

    $conn->query($sql);

    $message = "
Your account has been BANNED
from the AgaPay system.
";

    $notif = "
        INSERT INTO notifications
        (
            user_id,
            message
        )
        VALUES
        (
            '$id',
            '$message'
        )
    ";

    $conn->query($notif);

    header("Location: dashboard.php");
    exit();
}

// ==========================================
// GET USERS
// ==========================================
$users = $conn->query("
    SELECT *
    FROM users
    ORDER BY id DESC
");

?>

<!DOCTYPE html>
<html>
    <link rel="stylesheet" href="adminpanel.css">
<head>
    <title>AgaPay Admin Dashboard</title>
</head>

<body>

<h1>AgaPay Admin Dashboard</h1>

<table border="1" cellpadding="10">

<tr>
    <th>ID</th>
    <th>Name</th>
    <th>Contact</th>
    <th>Address</th>
    <th>Status</th>
    <th>Schedule Date</th>
    <th>Schedule Time</th>
    <th>Actions</th>
</tr>

<?php while($row = $users->fetch_assoc()) { ?>

<tr>

<td>
<?php echo $row['id']; ?>
</td>

<td>
<?php echo $row['name']; ?>
</td>

<td>
<?php echo $row['contact']; ?>
</td>

<td>
<?php echo $row['address']; ?>
</td>

<td>
<?php echo $row['status']; ?>
</td>

<form method="POST">

<td>

<input
type="date"
name="schedule_date"
required>

</td>

<td>

<input
type="time"
name="schedule_time"
required>

</td>

<td>

<input
type="hidden"
name="id"
value="<?php echo $row['id']; ?>">

<button name="approve">
Approve
</button>

<button name="reject">
Reject
</button>

<button name="ban">
Ban
</button>

</td>

</form>

</tr>

<?php } ?>

</table>
        <form method="POST" action="logout.php">
    <button type="submit" name="logout">
        <a href="admin.php">Logout</a>
    </button>
</form>
</body>
</html>