import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
// import TwitterLogo from "./images/twitter.svg";
// import OcadoLogo from "./images/logo_ocado_group_white.svg";

const ExternalLinks = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid item xs={3}>
          <a href="https://www.facebook.com">
            <img
              style={{ width: "100%" }}
              src="/images/facebook.svg"
              alt="Facebook"
            />
          </a>
        </Grid>
        <Grid item xs={3}>
          <img
            style={{ width: "100%" }}
            src="/images/twitter.svg"
            alt="Twitter"
          />
        </Grid>
        <Grid item xs={6}>
          <img
            src="/images/ocado.svg"
            alt="Ocado Group"
            style={{ width: "100%" }}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExternalLinks;
