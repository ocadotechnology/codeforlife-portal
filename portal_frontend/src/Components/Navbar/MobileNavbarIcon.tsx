import React from "react";
import { IconButtonStyled } from "./NavbarStyle";
import MobileNavbar from "./MobileNavbar";
import { User } from "../../App";

// TODO: Clean up these components
const MobileNavbarIcon = ({ userType, name }: User) => {
  return (
    <IconButtonStyled
      disableRipple={true}
      size="large"
      aria-label="account of current user"
      aria-controls="menu-appbar"
      aria-haspopup="true"
      color="inherit"
    >
      <MobileNavbar userType={userType} name={name} />
    </IconButtonStyled>
  );
};

export default MobileNavbarIcon;
