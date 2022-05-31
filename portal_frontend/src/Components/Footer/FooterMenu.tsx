import React from "react";

import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import { styled } from "@mui/material/styles";

const Item = styled("div")(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "left",
  fontWeight: "600",
  color: "#fff",
}));

const FooterMenu = () => {
  return (
    <Box sx={{ flexGrow: 1 }}>
      <Grid container rowSpacing={5}>
        <Grid item xs={4}>
          <Item>About us</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>Privacy policy</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>Home learning</Item>
        </Grid>
      </Grid>
      <Grid container rowSpacing={5}>
        <Grid item xs={4}>
          <Item>Help and support</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>Terms of use</Item>
        </Grid>
        <Grid item xs={4}>
          <Item>Get involved</Item>
        </Grid>
      </Grid>
      <Grid container rowSpacing={5}>
        <Grid item xs={4}>
          <Item>Cookie settings</Item>
        </Grid>
      </Grid>
    </Box>
  );
};

export default FooterMenu;
