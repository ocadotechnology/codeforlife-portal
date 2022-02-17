import React from "react";
import { MenuWrap } from "./NavbarStyle";
import { Button } from "@mui/material";
import { MenuItem } from "@mui/material";
import Menu from "@mui/material/Menu";
import { useState } from "react";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

type UserType = "student" | "independent" | "teacher";

interface Props {
  userType: UserType;
}

const SubMenu = ({ userType }: Props) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleUserType = (user: string) => {
    if (user === "student" || user === "teacher") {
      return ["Rapid Router", "Kurono"];
    } else if (user === "independent") {
      return ["Rapid Router"];
    } else return [];
  };
  const user: string[] = handleUserType(userType);
  return (
    <MenuWrap sx={{ flexGrow: 1 }}>
      <Button variant="text" color="inherit">
        {userType}
      </Button>
      <Button variant="text" color="inherit">
        Dashboard
      </Button>
      <Button variant="text" color="inherit" onClick={handleClick}>
        Games <ArrowDropDownIcon />
      </Button>
      <Button variant="text" color="inherit" onClick={handleClick}>
        {userType === "teacher" ? "Teaching Resources" : "Learning Resources"}{" "}
        <ArrowDropDownIcon />
      </Button>
      <Menu
        sx={{ width: "100%" }}
        id="basic-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          "aria-labelledby": "basic-button",
        }}
      >
        {user.map((user) => {
          return (
            <MenuItem
              sx={{
                margin: "0rem 13rem 0rem 0rem",
                width: "100%",
              }}
              onClick={handleClose}
            >
              {user}
            </MenuItem>
          );
        })}
      </Menu>
    </MenuWrap>
  );
};

export default SubMenu;
