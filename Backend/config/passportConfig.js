const passport = require("passport");
const LocalStrategy = require("passport-local").Strategy;
const bcrypt = require("bcryptjs");
const User = require("../models/User");

passport.use(
  new LocalStrategy(
    { usernameField: "emailOrUsername" }, // Change the field name to a more generic one
    async (emailOrUsername, password, done) => {
      try {
        // Find user by email or username
        const user = await User.findOne({
          $or: [{ email: emailOrUsername }, { username: emailOrUsername }],
        });
        if (!user) {
          console.log("User not found with email or username:", emailOrUsername); // Debug log
          return done(null, false, { message: "Incorrect email or username." });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (isMatch) {
          console.log("Password match for user:", emailOrUsername); // Debug log
          return done(null, user);
        } else {
          console.log("Incorrect password for user:", emailOrUsername); // Debug log
          return done(null, false, { message: "Incorrect password." });
        }
      } catch (err) {
        console.error("Error during authentication:", err); // Debug log
        return done(err);
      }
    }
  )
);

passport.serializeUser((user, done) => {
  done(null, user.id);
});

passport.deserializeUser(async (id, done) => {
  try {
    const user = await User.findById(id);
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});