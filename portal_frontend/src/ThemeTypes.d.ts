import { PaletteColorOptions } from "@mui/material";
import React from "react";

declare module "@mui/material/styles" {
  // allow configuration using `createTheme`
  interface PaletteOptions {
    tertiary?: PaletteColorOptions;
    student?: PaletterColorOptions;
    independent?: PaletteColorOptions;
    teacher?: PaletteColorOptions;
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
