import { Typography } from "@mui/material";
import React from "react";
import { UserType } from "../../App";

interface UserProps {
  userType: UserType;
}

const UserTypeTitle = ({ userType }: UserProps) => {
  return (
    <Typography
      variant="h4"
      sx={{
        marginLeft: "3vw",
        display: { xs: "none", sm: "none", md: "none", lg: "flex" },
        color: "text.primary"
      }}
    >
      {userType !== "none"
        ? userType.charAt(0).toUpperCase() + userType.slice(1)
        : null}
    </Typography>
  );
};

export default UserTypeTitle;
