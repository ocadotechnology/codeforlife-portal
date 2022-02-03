import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import FacebookLogo from "./images/facebook.svg";
import TwitterLogo from "./images/twitter.svg";
import OcadoLogo from "./images/logo_ocado_group_white.svg";

const ExternalLinks = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid item xs={3}>
          <a href="https://www.facebook.com">
            <img style={{ width: "100%" }} src={FacebookLogo} alt="Facebook" />
          </a>
        </Grid>
        <Grid item xs={3}>
          <img style={{ width: "100%" }} src={TwitterLogo} alt="Twitter" />
        </Grid>
        <Grid item xs={6}>
          <img src={OcadoLogo} alt="Ocado Group" style={{ width: "100%" }} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExternalLinks;
