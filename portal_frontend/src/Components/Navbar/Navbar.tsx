import {
  IconButtonStyled,
  AppBarStyled,
  ToolbarStyled,
  LogoCfl,
  LogoOcado,
} from "./NavbarStyle";
import { User } from "../../App";
import Dashboard from "./Dashboard";
import Games from "./Games";
import LearningResources from "./LearningResources";
import UserTypeTitle from "./UserTypeTitle";
import UserLogInButton from "./UserLogInButton";
import MobileNavbarIcon from "./MobileNavbarIcon";

export interface GamesProps {
  games: string[];
}

const Navbar = ({ userType, name }: User) => {
  return (
    <AppBarStyled position="fixed">
      <ToolbarStyled
        sx={{
          paddingRight: "1rem",
        }}
        disableGutters
      >
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
        <UserTypeTitle userType="independent" />
        <Dashboard />
        <Games games={["Rapid Router"]} />
        <LearningResources games={["Rapid Router"]} />
        <UserLogInButton name={name} />
        <MobileNavbarIcon userType={userType} name={name} />
      </ToolbarStyled>
    </AppBarStyled>
  );
};
export default Navbar;
