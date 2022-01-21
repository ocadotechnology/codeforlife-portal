import React from "react";
import { Box } from "@mui/material";
import Typography from "@mui/material/Typography";

interface Username {
	name: string;
}
const Welcome: React.FC<Username> = ({ name }) => {
	return (
		<Box
			sx={{
				display: "flex",
				flexDirection: "column",
				padding: "6rem 0 6rem 0",
				justifyContent: "center",
				bgcolor: "secondary.main",
				"& > h1, h4": {
					textAlign: "center",
				},
			}}
		>
			<Typography variant="h1">Welcome, {name}</Typography>
			<Typography variant="h4">
				This is where you can access your games
			</Typography>
		</Box>
	);
};

export default Welcome;
