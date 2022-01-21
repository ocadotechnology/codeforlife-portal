import React from "react";
import { Box, Card, Typography } from "@mui/material";
import { CardStyled, CardsStyled } from "./MeetTheCharactersStyle";
import { BoxStyled } from "./MeetTheCharactersStyle";

const NAMES = ["Xian", "Jools", "Zayed"];
const DESCRIPTIONS = [
	"Fun, active, will dance to just about anything that produces a beat. Has great memory, always a joke at hand, might try to introduce memes in Ancient Greece. Scored gold in a track race once and will take any opportunity to bring that up.",
	"A quick-witted kid who wasn’t expecting to embark in a time-warping journey but can’t say no to a challenge. Someone has to keep the rest of the group in check, after all!",
	"A pretty chill, curious soul that prefers practice to theory. Always ready to jump into an adventure if it looks interesting enough; not so much otherwise. Probably the one who accidentally turned the time machine on in first place.",
];
const IMAGES = [
	"https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Xian.png",
	"https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Jools.png",
	"https://storage.googleapis.com/codeforlife-assets/images/aimmo_characters/Zayed.png",
];

const Cards = () => {
	return (
		<CardsStyled>
			{NAMES.map((name, i) => {
				return (
					<CardStyled elevation={5}>
						<Typography variant="h5">{name}</Typography>
						<img src={IMAGES[i]} />
						<Typography variant="subtitle1">
							{DESCRIPTIONS[i]}
						</Typography>
					</CardStyled>
				);
			})}
		</CardsStyled>
	);
};

export default Cards;
