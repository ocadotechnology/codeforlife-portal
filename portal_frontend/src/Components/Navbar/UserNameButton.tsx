import React from "react";
import { UserNameButtonStyled } from "./NavbarStyle";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import { UserItemStyled, UserButtonDivStyled } from "./NavbarStyle";
import { UserMenuStyled } from "./NavbarStyle";

import LogoutIcon from "@mui/icons-material/Logout";
import ManageAccountsOutlinedIcon from "@mui/icons-material/ManageAccountsOutlined";
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";

import { User } from "../../App";

import { useEffect } from "react";




const logInSettings = {
  student: {
    navFieldText: ["Log out", "Change Password"],
    navFieldURLs: ["", ""],
    navFieldIcons: [<LogoutIcon />, <LockOutlinedIcon />],
  },
  independent: {
    navFieldText: ["Log out", "Update account details"],
    navFieldURLs: ["", ""],
    navFieldIcons: [<LogoutIcon />, <ManageAccountsOutlinedIcon />],
  },
  teacher: {
    navFieldText: ["Log out", "Update account details"],
    navFieldURLs: ["", ""],
    navFieldIcons: [<LogoutIcon />, <ManageAccountsOutlinedIcon />],
  },
  // This field is just so TypeScript
  // does not complain :)
  none: {
    navFieldText: [],
    navFieldURLs: [],
    navFieldIcons: [],
  },
};

const UserNameButton: React.FC<User> = ({ userType, userName }) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };
  // Bug where the open dropdown follows
  // window resize, so close it on resize

  const handleClose = () => {
    setAnchorEl(null);
  };

  useEffect(() => {
    const handleResize = () => {
      handleClose();
    };
    window.addEventListener("resize", handleResize);
  });
  return (
    <UserButtonDivStyled>
      <UserNameButtonStyled
        endIcon={<PersonOutlineIcon />}
        aria-controls={open ? "basic-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
      >
        {userName}
      </UserNameButtonStyled>
      <UserMenuStyled anchorEl={anchorEl} open={open} onClose={handleClose}>
        {logInSettings[userType].navFieldText.map(
          (element: string, i: number) => {
            return (
              <div>
                <UserItemStyled
                  onClick={handleClose}
                  endIcon={logInSettings[userType].navFieldIcons[i]}
                  href={logInSettings[userType].navFieldURLs[i]}
                >
                  {element}
                </UserItemStyled>
              </div>
            );
          }
        )}
      </UserMenuStyled>
    </UserButtonDivStyled>
  );
};

export default UserNameButton;
