import React from "react";
import { GamesProps } from "./Navbar";
import { useState, useEffect } from "react";
import { Box, Button, CardContent, Collapse, ListItem, Menu, Popover, Typography } from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import { ResponsiveDiv } from "./NavbarStyle";

const Games = ({ games }: GamesProps) => {
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);

  const handleOpen = (event: any) => {
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
    <ResponsiveDiv
      onMouseOverCapture={handleOpen}
      onMouseOutCapture={handleClose}
    >
      <Box

      >
        <Button
          sx={{
            fontWeight: "100",
            marginLeft: "2vw",
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
          endIcon={<KeyboardArrowDownIcon />}
        >
          Games
        </Button>
        <Collapse
          orientation="vertical"
          in={open}
        >
          <Box>
            <ListItem>
              {games.map((element) => {
                return (
                  <Typography
                    sx={{
                      background: "white",
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
            </ListItem>
          </Box>
        </Collapse>
      </Box>
    </ResponsiveDiv>
  );
};

export default Games;
/*
      <Menu
        anchorEl={anchorEl}
        keepMounted
        open={open}

        onMouseOutCapture={handleClose}
      >

      </Menu>*/