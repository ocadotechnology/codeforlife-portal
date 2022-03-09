import React from "react";
import Box from "@mui/material/Box";

import RRBackground from "img/rapid_router_landing_hero.png";
import RRLogo from "img/RR_logo.svg";

const RapidRouter = () => {
  return (
    <Box
      sx={{
        margin: "6rem 0 0 0",
        height: "320px",
        textAlign: "center",
        backgroundImage: `url(${RRBackground})`,
      }}
    >
      <Box
        component="img"
        sx={{ width: "25%" }}
        alt="Rapid Router logo"
        src={RRLogo}
      ></Box>
    </Box>
  );
};

export default RapidRouter;
