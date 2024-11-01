const express = require("express");
const passport = require("passport");
const bcrypt = require("bcryptjs");
const User = require("../models/User");

const router = express.Router();

router.post("/signup", (req, res) => {
  const { firstName, lastName, username, email, password } = req.body;
  console.log("Received signup request:", req.body); // Log the received data

  if (!password) {
    console.error("Password is missing");
    return res.status(400).json({ message: "Password is required" });
  }

  const newUser = new User({ firstName, lastName, username, email, password });

  bcrypt.genSalt(10, (err, salt) => {
    if (err) {
      console.error("Error generating salt:", err);
      return res.status(500).json({ message: "Server error" });
    }
    bcrypt.hash(newUser.password, salt, (err, hash) => {
      if (err) {
        console.error("Error hashing password:", err);
        return res.status(500).json({ message: "Server error" });
      }
      newUser.password = hash;
      newUser
        .save()
        .then((user) => res.status(201).json(user))
        .catch((err) => {
          console.error("Error saving user:", err);
          res.status(400).json({ message: "User already exists" });
        });
    });
  });
});

router.post("/login", (req, res, next) => {
  passport.authenticate("local", (err, user, info) => {
    if (err) {
      console.error("Authentication error:", err); // Debug log
      return next(err);
    }
    if (!user) {
      console.log("Authentication failed:", info.message); // Debug log
      return res.status(401).json({ message: info.message });
    }
    req.logIn(user, (err) => {
      if (err) {
        console.error("Login error:", err); // Debug log
        return next(err);
      }
      return res.json({ message: "Login successful" });
    });
  })(req, res, next);
});

router.get("/logout", (req, res) => {
  req.logout();
  res.json({ message: "Logged out" });
});

module.exports = router;
