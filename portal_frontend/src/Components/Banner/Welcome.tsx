import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";

interface User {
  name: string;
  userType: string;
}
const Welcome = ({ name, userType }: User) => {
  let bgcolor, color;
  if (userType === "independent") {
    bgcolor = "secondary.main";
    color = "secondary.contrastText";
  } else if (userType === "teacher") {
    bgcolor = "primary.main";
    color = "primary.contrastText";
  } else if (userType === "student") {
    bgcolor = "tertiary.main";
    color = "tertiary.contrastText";
  }

  const subtitle =
    userType === "teacher" ? (
      ""
    ) : (
      <Typography variant="h4">
        This is where you can access your games
      </Typography>
    );

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "320px",
        justifyContent: "center",
        alignItems: "center",
        bgcolor: bgcolor,
        color: color,
      }}
    >
      <Typography variant="h1">Welcome, {name}</Typography>
      {subtitle}
    </Box>
  );
};

export default Welcome;
