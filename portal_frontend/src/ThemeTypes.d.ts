
import React from "react"


declare module '@mui/material/styles' {
  interface TypographyVariants {
    poster: React.CSSProperties;
    quote: React.CSSProperties;
    bodyText1: React.CSSProperties;
    bodyText2: React.CSSProperties;
    buttonText: React.CSSProperties;
  }

  // allow configuration using `createTheme`
  interface TypographyVariantsOptions {
    poster?: React.CSSProperties;
    quote?: React.CSSProperties;
    bodyText1?: React.CSSProperties;
    bodyText2?: React.CSSProperties;
    buttonText?: React.CSSProperties;
  }
}

// Update the Typography's variant prop options
declare module '@mui/material/Typography' {
  interface TypographyPropsVariantOverrides {
    poster: true;
    quote: true;
    bodyText1: true;
    bodyText2: true;
    buttonText: true;
  }
}