document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let role = document.getElementById("role").value; // Assuming a dropdown/select input for role

    // User database
    const users = [
        { username: "admin", password: "admin123", role: "patient" },
        { username: "Shone", password: "shone123", role: "patient" },
        { username: "care", password: "care123", role: "caretaker" },
        { username: "doct", password: "doct123", role: "doctor" }
    ];

    // Find user in the database
    const user = users.find(u => u.username === username && u.password === password && u.role === role);

    if (user) {
        sessionStorage.setItem("username", user.username);
        sessionStorage.setItem("role", user.role);
        window.location.href = "home.html";
    } else {
        document.getElementById("error-message").innerText = "Invalid credentials or role!";
    }
});