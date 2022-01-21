import React from "react";
import { Typography } from "@mui/material";
import { BoxStyled, CardStyled, ButtonStyled } from "./YourGamesStyle";

const YourGames = () => {
	return (
		<BoxStyled>
			<Typography variant="h4">Your games</Typography>
			<CardStyled elevation={3}>
				<img
					src="https://geekyteacher204.files.wordpress.com/2018/04/rapidrouter-logo.png"
					alt="RR logo"
				/>
				<Typography variant="h5">Rapid Router</Typography>
				<Typography variant="body1">
					Rapid Router guides you, and makes learning to code easy and
					great fun. Using Blockly, you can advance through the levels
					to become an Ocado delivery hero.
				</Typography>
				<ButtonStyled variant="contained" color="secondary">
					Play
				</ButtonStyled>
			</CardStyled>
		</BoxStyled>
	);
};

export default YourGames;
