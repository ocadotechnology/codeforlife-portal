/*

Libraries that seem to be breaking the app without notice

@material-ui/core
@mui/lab


*/

import React from "react";
import theme from "./Theme";
import { ThemeProvider } from "@mui/material/styles";
import Navbar from "./Components/Navbar/Navbar";
import Welcome from "./Components/Banner/Welcome";
import RapidRouter from "./Components/Banner/RapidRouter";
import YourGames from "./Components/YourGames/YourGames";
import RapidRouterScores from "./Components/RapidRouterScores/RapidRouterScores";
import KuronoWidget from "./Components/KuronoWidget/KuronoWidget";
import MeetTheCharacters from "./Components/MeetTheCharacters/MeetTheCharacters";

type UserType = "student" | "independent" | "teacher";

let name: string = "Ada";
let userType: UserType = "independent";

const App = () => {
  return (
    <div>
      <ThemeProvider theme={theme}>
        <Navbar userType={userType} userName={name} />
        <Welcome name={name} userType={userType} />
        <RapidRouterScores />
        <KuronoWidget />
        <MeetTheCharacters />
      </ThemeProvider>
    </div>
  );
};

export default App;
