import {
  IconButtonStyled,
  AppBarStyled,
  ToolbarStyled,
  LogoCfl,
  LogoOcado,
} from "./NavbarStyle";
import NavbarActions from "./NavbarActions";
import UserNameButton from "./UserNameButton";
import NotLoggedIn from "./NotLoggedIn";
import MobileNavbar from "./MobileNavbar";
import { User } from "../../App";

const Navbar = ({ userType, name }: User) => {
  return (
    <AppBarStyled position="fixed">
      <ToolbarStyled disableGutters>
        <a href="http://www.localhost:3000">
          <LogoCfl src="/images/navbar/logo_cfl.png" />
        </a>
        <a
          href="https://www.ocadogroup.com/our-responsible-business/corporate-responsibility/skills-for-the-future"
          target="_blank"
          rel="noreferrer"
        >
          <LogoOcado src="/images/navbar/logo_ocado_group.svg" />
        </a>
        <NavbarActions userType={userType} name={name} />
        {userType === "none" ? (
          <NotLoggedIn />
        ) : (
          <UserNameButton userType={userType} name={name} />
        )}
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
      </ToolbarStyled>
    </AppBarStyled>
  );
};
export default Navbar;
