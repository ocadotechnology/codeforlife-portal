import Box from "@mui/material/Box";
import Grid from "@mui/material/Grid";
import { Container } from "@mui/material";
import ExternalLinks from "./ExternalLinks";
import FooterMenu from "./FooterMenu";

const style = {
	background: "rgb(224, 0, 77)",
};

const Footer = () => {
	return (
		<div style={style}>
			<Container>
				<Box sx={{ flexGrow: 1 }}>
					<Grid container spacing={2}>
						<Grid item xs={8}>
							<FooterMenu />
						</Grid>
						<Grid item xs={4}>
							<img
								style={{
									width: "100%",
								}}
								src="https://www.codeforlife.education/static/portal/img/logo_cfl_white_landscape.png"
								alt="Code for Life logo"
							/>
							<ExternalLinks />
						</Grid>
						<Grid item xs={9}></Grid>
					</Grid>
				</Box>
			</Container>
		</div>
	);
};

export default Footer;
