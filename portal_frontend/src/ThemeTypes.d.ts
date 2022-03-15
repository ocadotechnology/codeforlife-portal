import { PaletteColorOptions } from "@mui/material";
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
