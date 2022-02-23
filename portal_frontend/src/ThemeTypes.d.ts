import React from "react";

declare module "@mui/material/styles" {
  interface PaletteVariantOptions {
    default?: React.CSSProperties;
  }
  declare module "@mui/material/Palette" {
    interface PalettePropsVariantOverrides {
      default: true;
    }
  }
  // allow configuration using `createTheme`
  interface TypographyVariantsOptions {
    quote?: React.CSSProperties;
  }
}

// Update the Typography's variant prop options
declare module "@mui/material/Typography" {
  interface TypographyPropsVariantOverrides {
    quote: true;
  }
}

declare module "@mui/material/styles" {
  interface Palette {
    neutral: Palette["primary"];
  }

  // allow configuration using `createTheme`
  interface PaletteOptions {
    neutral?: PaletteOptions["primary"];
  }
}

// Update the Button's color prop options
declare module "@mui/material/Button" {
  interface ButtonPropsColorOverrides {
    neutral: true;
  }
}
