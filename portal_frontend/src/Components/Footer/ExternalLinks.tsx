import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";

import facebookLogo from "img/footer/facebook.svg";
import twitterLogo from "img/footer/twitter.svg";
import ocadoLogoWhite from "img/footer/ocado.svg";

const ExternalLinks = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid item xs={3}>
          <a href="https://www.facebook.com/codeforlifeuk/">
            <img style={{ width: "100%" }} src={facebookLogo} alt="Facebook" />
          </a>
        </Grid>
        <Grid item xs={3}>
          <img style={{ width: "100%" }} src={twitterLogo} alt="Twitter" />
        </Grid>
        <Grid item xs={6}>
          <img
            src={ocadoLogoWhite}
            alt="Ocado Group"
            style={{ width: "100%" }}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExternalLinks;
