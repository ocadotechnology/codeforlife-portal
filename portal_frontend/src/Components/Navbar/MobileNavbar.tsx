import * as React from "react";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";
import ListItemIcon from "@mui/material/ListItemIcon";
import { User } from "../../App";
import {
  DrawerStyled,
  LinkTypography,
  ListSingleItem,
  ListStyled,
  MenuIconButtonStyled,
  MobileMenuBarUserName,
} from "./NavbarStyle";
import MenuIcon from "@mui/icons-material/Menu";

import CookieOutlinedIcon from "@mui/icons-material/CookieOutlined";
import HelpOutlineOutlinedIcon from "@mui/icons-material/HelpOutlineOutlined";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import PrivacyTipOutlinedIcon from "@mui/icons-material/PrivacyTipOutlined";
import GavelOutlinedIcon from "@mui/icons-material/GavelOutlined";
import LocalLibraryOutlinedIcon from "@mui/icons-material/LocalLibraryOutlined";
import PanToolOutlinedIcon from "@mui/icons-material/PanToolOutlined";
import ManageAccountsOutlinedIcon from "@mui/icons-material/ManageAccountsOutlined";
import LogoutOutlinedIcon from "@mui/icons-material/LogoutOutlined";

import CloseIcon from "@mui/icons-material/Close";
import SmallReactiveMenu from "./MobileMenu";

const MobileNavbar = ({ userType, name }: User) => {
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

  const list = (anchor: any) => (
    <Box
      sx={{
        width: anchor === "top" || anchor === "bottom" ? "auto" : 250,
      }}
    >
      <MobileMenuBarUserName variant="h3">
        {userType !== "none" ? name : null}
      </MobileMenuBarUserName>
      <SmallReactiveMenu name={name} userType={userType} />
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
        {userType !== "none"
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
export default MobileNavbar;
