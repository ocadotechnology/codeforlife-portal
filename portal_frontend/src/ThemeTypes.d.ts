import React from "react";

declare module "@mui/material/styles" {
  // allow configuration using `createTheme`
  interface PaletteOptions {
    tertiary?: PaletteColorOptions;
  }
  interface TypographyVariantsOptions {
    quote?: React.CSSProperties;
  }
}

declare module "@mui/material/Button" {
  interface ButtonPropsColorOverrides {
    neutral: true;
  }
}