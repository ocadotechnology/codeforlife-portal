import React from "react";
import { Link } from "@mui/material";

const Dashboard = () => {
  return (
    <Link
      href=""
      variant="body1"
      sx={{
        marginLeft: "3rem",
        color: "black",
        textDecoration: "none",
        "&:hover": {
          textDecoration: "underline",
        },
        display: { xs: "none", sm: "none", md: "none", lg: "flex" },
      }}
    >
      Dashboard
    </Link>
  );
};

export default Dashboard;
