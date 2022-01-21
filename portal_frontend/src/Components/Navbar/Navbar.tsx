import { MenuStyled } from "./NavbarStyle";
import React from "react";
import { Toolbar } from "@mui/material";
import { Button } from "@mui/material";
import { NavBarStyled, MenuIconStyled } from "./NavbarStyle";
import { Typography } from "@mui/material";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import { useState } from "react";
import { MenuWrap } from "./NavbarStyle";
import MenuIconNavBar from "./MenuIconNavBar";
import UserButton from "./UserButton";
import { userInfo } from "os";
import SubMenu from "./SubMenu";

type UserType = "student" | "independent" | "teacher";

interface Props {
	name: string;
	userType: UserType;
}

const Navbar = ({ name, userType }: Props) => {
	return (
		<Toolbar sx={{ display: "flex" }}>
			<NavBarStyled elevation={5}>
				<img
					src="https://www.codeforlife.education/static/portal/img/logo_cfl.png"
					alt="somethigns"
					style={{
						height: "80px",
					}}
				/>
				<img
					style={{
						height: "150px",
					}}
					src="https://image.pitchbook.com/J9YjXxMlKawW33vJmEuU86TyL8V1625027225121_200x200"
					alt="hello"
				/>
				<SubMenu userType={userType} />

				<MenuIconNavBar />
				<UserButton name={name} />
			</NavBarStyled>
		</Toolbar>
	);
};

export default Navbar;
