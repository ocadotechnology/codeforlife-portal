import * as React from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import { User } from "./Navbar";
import { useEffect } from "react";
import {
  DrawerStyled,
  LinkStyled,
  LinkTypography,
  ListItemIconStyled,
  ListSingleItem,
  ListStyled,
  MenuIconButtonStyled,
  SmallMenuBarUserName,
  SmallNavbarRegisterButton,
  TypographyHover,
} from "./NavbarStyle";
import MenuIcon from "@mui/icons-material/Menu";

import LoginOutlinedIcon from "@mui/icons-material/LoginOutlined";
import GridViewOutlinedIcon from "@mui/icons-material/GridViewOutlined";
import CookieOutlinedIcon from "@mui/icons-material/CookieOutlined";
import SportsEsportsOutlinedIcon from "@mui/icons-material/SportsEsportsOutlined";
import ArticleOutlinedIcon from "@mui/icons-material/ArticleOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import PrivacyTipOutlinedIcon from "@mui/icons-material/PrivacyTipOutlined";
import GavelOutlinedIcon from "@mui/icons-material/GavelOutlined";
import LocalLibraryOutlinedIcon from "@mui/icons-material/LocalLibraryOutlined";
import PanToolOutlinedIcon from "@mui/icons-material/PanToolOutlined";
import ManageAccountsOutlinedIcon from "@mui/icons-material/ManageAccountsOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";
import { RegisterButtonSmallMenuStyled } from "./NavbarStyle";
import SchoolOutlinedIcon from "@mui/icons-material/SchoolOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";

import { ListItemStyled } from "./NavbarStyle";
import CloseIcon from "@mui/icons-material/Close";
import { Button, Link, Typography } from "@mui/material";
import LogInButton from "./LogInButton";
import RegisterButton from "./RegisterButton";
import Collapse from "@mui/material/Collapse";
import SmallReactiveMenu from "./SmallReactiveMenu";

const SmallNavbar: React.FC<User> = ({ userType, userName }) => {
  const staticContent = [
    "About us",
    "Help and support",
    "Cookie settings",
    "Privacy policy",
    "Terms of use",
    "Home learning",
    "Get involved",
  ];

  const staticContentLinks = [
    "https://www.codeforlife.education/about",
    "",
    "",
    "https://www.codeforlife.education/privacy-policy/",
    "https://www.codeforlife.education/terms",
    "https://www.codeforlife.education/home-learning",
    "https://www.codeforlife.education/getinvolved",
  ];

  const staticContentIcons = [
    <InfoOutlinedIcon />,
    <HelpOutlineOutlinedIcon />,
    <CookieOutlinedIcon />,
    <PrivacyTipOutlinedIcon />,
    <GavelOutlinedIcon />,
    <LocalLibraryOutlinedIcon />,
    <PanToolOutlinedIcon />,
  ];

  const accountContent = ["Update account details", "Logout"];

  const accountLinks = ["", ""];

  const accountContentIcons = [
    <ManageAccountsOutlinedIcon />,
    <LogoutOutlinedIcon />,
  ];

  const [state, setState] = React.useState({
    top: false,
  });

  const toggleDrawer =
    (anchor: "top", open: boolean) =>
    (event: React.KeyboardEvent | React.MouseEvent) => {
      if (
        event.type === "keydown" &&
        ((event as React.KeyboardEvent).key === "Tab" ||
          (event as React.KeyboardEvent).key === "Shift")
      ) {
        return;
      }

      setState({ ...state, [anchor]: open });
    };

  const handleClick = () => {
    toggleDrawer("top", true);
    setState({
      ...state,
      top: !state["top"],
    });
  };

  const list = (anchor: any) => (
    <Box
      sx={{
        width: anchor === "top" || anchor === "bottom" ? "auto" : 250,
      }}
    >
      <SmallMenuBarUserName variant="h3">
        {userType !== "None" ? userName : null}
      </SmallMenuBarUserName>
      <SmallReactiveMenu userType={userType} />
      <Divider />
      <ListStyled>
        {staticContent.map((text, index) => (
          <ListSingleItem>
            <ListItemIcon>{staticContentIcons[index]}</ListItemIcon>
            <LinkTypography
              underline="hover"
              href={staticContentLinks[index]}
              variant="subtitle2"
            >
              {text}
            </LinkTypography>
          </ListSingleItem>
        ))}
      </ListStyled>
      <Divider />
      <ListStyled>
        {userType !== "None"
          ? accountContent.map((text: string, index: number) => {
              return (
                <ListSingleItem>
                  <ListItemIcon>{accountContentIcons[index]}</ListItemIcon>
                  <LinkTypography
                    href={accountLinks[index]}
                    underline="hover"
                    variant="subtitle2"
                  >
                    {text}
                  </LinkTypography>
                </ListSingleItem>
              );
            })
          : null}
      </ListStyled>
    </Box>
  );
  // Bug where the open dropdown follows
  // window resize, so close it on resize

  return (
    <div>
      <React.Fragment>
        <MenuIconButtonStyled
          disableRipple={true}
          onClick={toggleDrawer("top", !state["top"])}
        >
          {state["top"] ? <CloseIcon /> : <MenuIcon />}
        </MenuIconButtonStyled>
        <DrawerStyled
          anchor={"top"}
          open={state["top"]}
          onClose={() => setState({ top: false })}
        >
          {list("top")}
        </DrawerStyled>
      </React.Fragment>
    </div>
  );
};
export default SmallNavbar;
/*
            <ListStyled >
                {userType !== "None" ?
                    <ListItem onClick={handleClick}
                    >
                        <ListItemIcon>
                            {userType === "Teacher" ? <PersonOutlinedIcon /> : <SchoolOutlinedIcon />}
                        </ListItemIcon>
                        <ListItemText primary={userType} />
                    </ListItem>
                    :
                    <div>
                        <RegisterButton
                        />
                        <div onClick={handleClick}>
                            <LogInButton small={true} />
                        </div>
                    </div>
                }
                <Collapse in={state["menu"]} >

                    {dynamicContent[userType].navField.text.map((text, index) => (
                        <div
                            onClick={() => toggleDrawer(anchor, false)}
                        >
                            <ListItemStyled
                                userType={userType}
                                key={text}>
                                <ListItemIconStyled userType={userType}>
                                    {dynamicContentIcons[index]}
                                </ListItemIconStyled>
                                {
                                    text === "Dashboard" || text === "Scoreboard" ?
                                        <ListItemText primary={text} /> :
                                        <div>
                                            <ListItemText primary={text} />
                                            <Collapse in={state[text === "Games" ? "games" : "resources"]}>
                                                <ListItemStyled userType={userType}>

                                                    {dynamicContent[userType].games.text.map((element: string) => {
                                                        return <Typography variant='body1'>{element}</Typography>
                                                    })}
                                                </ListItemStyled>
                                            </Collapse>
                                        </div>
                                }
                            </ListItemStyled>
                        </div>
                    ))
                    }
                </Collapse>
            </ListStyled>*/
