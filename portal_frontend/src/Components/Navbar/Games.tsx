import React from "react";
import { GamesProps } from "./Navbar";
import { useState, useEffect } from "react";
import { Box, Button, Collapse, Popover, Typography } from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

const Games = ({ games }: GamesProps) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);
  const id = open ? "simple-popover" : undefined;

  useEffect(() => {
    // Bug where the open dropdown follows window resize, so close it on resize
    const handleResize = () => {
      handleClose();
    };
    window.addEventListener("resize", handleResize);
  });

  return (
    <Box
      sx={{
        display: { xs: "none", sm: "none", md: "none", lg: "flex" },
      }}
    >
      <Button
        sx={{
          fontWeight: "100",
          marginLeft: "1vw",
          background: "white",
          color: "black",
          boxShadow: "none",
          textTransform: "none",
          "&:hover": {
            background: "white",
            color: "black",
            textDecoration: "underline",
            boxShadow: "none",
          },
        }}
        aria-describedby={id}
        variant="contained"
        onClick={handleClick}
        endIcon={<KeyboardArrowDownIcon />}
      >
        Games
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
      >
        {games.map((element) => {
          return (
            <Typography
              sx={{
                p: 2,
                "&:hover": {
                  textDecoration: "underline",
                  cursor: "pointer",
                },
              }}
            >
              {element}
            </Typography>
          );
        })}
      </Popover>
    </Box>
  );
};

export default Games;
