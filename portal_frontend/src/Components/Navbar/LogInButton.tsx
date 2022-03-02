import * as React from "react";
import { useState, useEffect } from "react";
import {
  LogInButtonStyled,
  LogInMenuStyled,
  SubButtonStyled,
} from "./NavbarStyle";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import { BorderBottom } from "@mui/icons-material";
import theme from "../../Theme";

interface ScreenProps {
  smallScreen?: Boolean;
}

export const LogInButton = ({ smallScreen }: ScreenProps) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const [bottomBorder, setBorder] = useState(
    `2px solid ${theme.palette.secondary.main}`
  );

  const handleClose = () => {
    setAnchorEl(null);
    setBorder(`2px solid ${theme.palette.secondary.main}`);
  };

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
    setBorder("none");
  };
  useEffect(() => {
    // Bug where the open dropdown follows window resize, so close it on resize
    const handleResize = () => {
      handleClose();
    };
    window.addEventListener("resize", handleResize);
  });

  return (
    <div>
      <LogInButtonStyled
        aria-controls={open ? "basic-menu" : undefined}
        aria-haspopup="true"
        aria-expanded={open ? "true" : undefined}
        onClick={handleClick}
        endIcon={<KeyboardArrowDownIcon />}
        sx={{
          borderBottom: bottomBorder,
        }}
      >
        Log in
      </LogInButtonStyled>
      {smallScreen ? null : (
        <LogInMenuStyled anchorEl={anchorEl} open={open} onClose={handleClose}>
          <SubButtonStyled onClick={handleClose}>
            Teacher <ChevronRightIcon />
          </SubButtonStyled>
          <SubButtonStyled onClick={handleClose}>
            Student <ChevronRightIcon />
          </SubButtonStyled>
          <SubButtonStyled onClick={handleClose}>
            Independent <ChevronRightIcon />
          </SubButtonStyled>
        </LogInMenuStyled>
      )}
    </div>
  );
};

export default LogInButton;
