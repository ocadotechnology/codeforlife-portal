import { Typography, Box, Paper } from "@mui/material";
import React from "react";
import { PaperStyled, StyledBox } from "./KuronoWidgetStyle";

// For this component to work you need to run the
// portal since the video is src from localhost:8000

const KuronoWidget = () => {
  return (
    <StyledBox>
      <img
        src="http://localhost:8000/static/portal/img/kurono_logo.svg"
        alt="kurono logo"
      />
      <Typography variant="h4">
        Kurono is only available as part of a school or club. Your teacher,
        parent or guardian can set up a club for you and create a class.
      </Typography>
      <PaperStyled elevation={4}>
        <video width="1200" height="675" loop autoPlay>
          <source src="http://localhost:8000/static/portal/video/aimmo_play_now_background_video.mp4" />
        </video>
      </PaperStyled>
    </StyledBox>
  );
};

export default KuronoWidget;
