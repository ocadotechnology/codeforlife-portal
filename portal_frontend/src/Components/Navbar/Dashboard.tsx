import React from "react";
import { Link } from "@mui/material";

const Dashboard = () => {
  return (
    <Link
      href=""
      variant="button"
      sx={{
        marginLeft: "3rem",
        color: "black",
        textDecoration: "none",
        textTransform: "none",
        fontWeight: "100",
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
