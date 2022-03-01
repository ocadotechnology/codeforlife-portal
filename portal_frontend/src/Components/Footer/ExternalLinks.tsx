import React from "react";
import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";

const ExternalLinks = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container spacing={2}>
        <Grid item xs={3}>
          <a href="https://www.facebook.com">
            <img
              style={{ width: "100%" }}
              src="/images/footer/facebook.svg"
              alt="Facebook"
            />
          </a>
        </Grid>
        <Grid item xs={3}>
          <img
            style={{ width: "100%" }}
            src="/images/footer/twitter.svg"
            alt="Twitter"
          />
        </Grid>
        <Grid item xs={6}>
          <img
            src="/images/footer/ocado.svg"
            alt="Ocado Group"
            style={{ width: "100%" }}
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ExternalLinks;
