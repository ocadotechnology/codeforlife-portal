import React from "react";
import { UserNameButtonStyled } from "./NavbarStyle";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import { UserItemStyled, UserButtonDivStyled } from "./NavbarStyle";
import { UserMenuStyled } from "./NavbarStyle";

import LogoutIcon from "@mui/icons-material/Logout";
import ManageAccountsOutlinedIcon from "@mui/icons-material/ManageAccountsOutlined";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";

import { User } from "../../App";

import { useEffect, useState } from "react";
import theme from "../../Theme";

const logInSettings = {
  student: [
    {
      navFieldText: "Log out",
      navFieldURLs: "",
      navFieldIcons: <LogoutIcon />,
    },
    {
      navFieldText: "Change Password",
      navFieldURLs: "",
      navFieldIcons: <LockOutlinedIcon />,
    },
  ],
  independent: [
    {
      navFieldText: "Log out",
      navFieldURLs: "",
      navFieldIcons: <LogoutIcon />,
    },
    {
      navFieldText: "Update account details",
      navFieldURLs: "",
      navFieldIcons: <ManageAccountsOutlinedIcon />,
    },
  ],
  teacher: [
    {
      navFieldText: "Log out",
      navFieldURLs: "",
      navFieldIcons: <LogoutIcon />,
    },
    {
      navFieldText: "Update account details",
      navFieldURLs: "",
      navFieldIcons: <ManageAccountsOutlinedIcon />,
    },
  ],
  // This field is just so TypeScript
  // does not complain :)
  none: [
    {
      navFieldText: "",
      navFieldURLs: "",
      navFieldIcons: <></>,
    },
  ],
};

const UserNameButton = ({ userType, name }: User) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const [bottomBorder, setBorder] = useState(
    `2px solid ${theme.palette.secondary.main}`
  );
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    setBorder("none");
  };

  const handleClose = () => {
    setAnchorEl(null);
    setBorder(`2px solid ${theme.palette.secondary.main}`);
  };

  useEffect(() => {
    // Bug where the open dropdown follows window resize, so close it on resize
    const handleResize = () => {
      handleClose();
    };
    window.addEventListener("resize", handleResize);
  });

  return (
    <UserButtonDivStyled>
      <UserNameButtonStyled
        style={{ borderBottom: bottomBorder }}
        endIcon={<PersonOutlineIcon />}
        aria-controls={open ? "basic-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        {name}
      </UserNameButtonStyled>
      <UserMenuStyled anchorEl={anchorEl} open={open} onClose={handleClose}>
        {logInSettings[userType].map((element) => {
          return (
            <UserItemStyled
              onClick={handleClose}
              endIcon={element.navFieldIcons}
              href={element.navFieldURLs}
            >
              {element.navFieldText}
            </UserItemStyled>
          );
        })}
      </UserMenuStyled>
    </UserButtonDivStyled>
  );
};

export default UserNameButton;
