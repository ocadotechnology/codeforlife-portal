import { Button, Popover, Typography } from "@mui/material";
import React from "react";
import theme from "../../Theme";
import KeyboardArrowDown from "@mui/icons-material/KeyboardArrowDown";
import { KeyboardArrowRight } from "@mui/icons-material";
import ManageAccountsOutlinedIcon from "@mui/icons-material/ManageAccountsOutlined";
import LogoutIcon from "@mui/icons-material/Logout";
import { useEffect } from "react";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";

interface NameProps {
  name: string;
}

const UserLogInButton = ({ name }: NameProps) => {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(
    null
  );

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;

  const buttonContent = [
    { buttonText: "Log out", buttonIcon: <LogoutIcon /> },
    {
      buttonText: "Update account details",
      buttonIcon: <ManageAccountsOutlinedIcon />,
    },
  ];

  useEffect(() => {
    // Bug where the open dropdown follows window resize, so close it on resize
    const handleResize = () => {
      handleClose();
    };
    window.addEventListener("resize", handleResize);
  });

  return (
    <>
      <Button
        onClick={handleClick}
        color="secondary"
        variant="outlined"
        endIcon={<PersonOutlineOutlinedIcon />}
        sx={{
          display: { xs: "none", sm: "none", md: "none", lg: "flex" },
          justifyContent: "space-between",
          marginLeft: "auto",
          width: "17vw",
          border: `2px solid ${theme.palette.secondary.main}`,
          color: "black",
          textTransform: "none",
          borderRadius: "0",
          "&:hover": {
            border: `2px solid ${theme.palette.secondary.main}`,
            background: "none",
            textDecoration: "underline",
          },
        }}
      >
        {name}
      </Button>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        sx={{
          "& > div": {
            borderRadius: "0",
          },
        }}
      >
        {buttonContent.map((element) => {
          return (
            <Button
              color="secondary"
              variant="outlined"
              endIcon={element.buttonIcon}
              sx={{
                display: "flex",
                justifyContent: "space-between",
                width: { md: "14.5vw", lg: "17vw" },
                borderLeft: `2px solid ${theme.palette.secondary.main}`,
                borderRight: `2px solid ${theme.palette.secondary.main}`,
                borderBottom: `2px solid ${theme.palette.secondary.main}`,
                color: "black",
                textTransform: "none",
                borderRadius: "0",
                fontSize: "14px",
                fontWeight: "100",
                textAlign: "left",
                "&:hover": {
                  background: "none",
                  borderLeft: `2px solid ${theme.palette.secondary.main}`,
                  borderRight: `2px solid ${theme.palette.secondary.main}`,
                  borderBottom: `2px solid ${theme.palette.secondary.main}`,
                  textDecoration: "underline",
                },
              }}
            >
              {element.buttonText}
            </Button>
          );
        })}
      </Popover>
    </>
  );
};

export default UserLogInButton;
