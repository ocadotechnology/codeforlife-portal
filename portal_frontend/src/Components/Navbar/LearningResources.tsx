import React from "react";
import { GamesProps } from "./Navbar";
import { useState } from "react";
import { Box, Button, Popover, Typography } from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

const LearningResources = ({ games }: GamesProps) => {
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

  return (
    <Box
      sx={{
        display: { xs: "none", sm: "none", md: "none", lg: "flex" },
      }}
    >
      <Button
        sx={{
          paddingLeft: "0",
          paddingRight: "0",
          marginLeft: "1vw",
          fontWeight: "100",
          marginLeddft: "0rem",
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
        Learning Resources
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
          return <Typography sx={{ p: 2 }}>{element}</Typography>;
        })}
      </Popover>
    </Box>
  );
};

export default LearningResources;
