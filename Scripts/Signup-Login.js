const navbarMenu = document.querySelector(".navbar .links");
const hamburgerBtn = document.querySelector(".hamburger-btn");
const hideMenuBtn = navbarMenu.querySelector(".close-btn");
const showPopupBtn = document.querySelector(".login-btn");
const formPopup = document.querySelector(".form-popup");
const hidePopupBtn = formPopup.querySelector(".close-btn");
const signupLoginLink = formPopup.querySelectorAll(".bottom-link a");

// Show mobile menu
hamburgerBtn.addEventListener("click", () => {
  navbarMenu.classList.toggle("show-menu");
});

// Hide mobile menu
hideMenuBtn.addEventListener("click", () => hamburgerBtn.click());

// Show login popup
showPopupBtn.addEventListener("click", () => {
  document.body.classList.toggle("show-popup");
});

// Hide login popup
hidePopupBtn.addEventListener("click", () => {
  document.body.classList.remove("show-popup");
});

// Show or hide signup form
signupLoginLink.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();
    formPopup.classList.toggle("show-signup", link.id === "signup-link");
  });
});

// Handle signup form submission
const signupForm = document.querySelector(".form-box.signup form");
signupForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(signupForm);
  const mappedData = {
    firstName: formData.get("firstname"),
    lastName: formData.get("lastname"),
    username: formData.get("username"),
    email: formData.get("email"),
    password: formData.get("password"),
  };

  console.log("Signup form data:", mappedData);

  try {
    const response = await fetch("http://localhost:5000/auth/signup", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(mappedData),
      credentials: "include",
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Signup failed");
    }

    const data = await response.json();
    console.log("Signup successful:", data);
    window.location.href = "hello.html";
  } catch (error) {
    console.error("Signup error:", error);
    alert(error.message || "Signup failed. Please try again.");
  }
});

// Handle login form submission
const loginForm = document.querySelector(".form-box.login form");
loginForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(loginForm);
  const mappedData = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  console.log("Form Data before mapping:", mappedData); // Debug log

  try {
    const response = await fetch("http://localhost:5000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(mappedData),
      credentials: "include",
    });

    if (!response.ok) {
      const errorData = await response.text(); // Use .text() for non-JSON responses
      throw new Error(errorData || "Login failed");
    }

    const data = await response.json();
    console.log("Login successful:", data);
    window.location.href = "hello.html";
  } catch (error) {
    console.error("Login error:", error);
    alert(error.message || "Login failed. Please try again.");
  }
});
