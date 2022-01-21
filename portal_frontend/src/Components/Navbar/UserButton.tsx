import { Button } from "@mui/material";
import React from "react";
import PersonOutlineIcon from "@mui/icons-material/PersonOutline";
import { UserButtonStyled } from "./NavbarStyle";

interface Username {
	name: string;
}

const UserButton = (props: Username) => {
	return (
		<UserButtonStyled color="secondary" variant="outlined">
			{props.name} <PersonOutlineIcon />
		</UserButtonStyled>
	);
};

export default UserButton;
