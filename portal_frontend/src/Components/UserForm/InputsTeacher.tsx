import { form } from "./LogInFormStyle";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { Box, Button, Checkbox, Typography } from "@mui/material";
import { FormControlLabel } from "@mui/material";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { TextField } from "@mui/material";
import SecurityIcon from "@mui/icons-material/Security";

const InputsTeacher = () => {
	const inputStyles = form();

	return (
		<Card className={inputStyles.inputForm}>
			<CardContent>
				<Typography variant="h4">Teacher/Tutor</Typography>
				<Typography variant="subtitle1">
					Once you've registered your personal details and logged in
					you'll be able to create your own school or club, or join
					other teachers at your institution:).
				</Typography>
				<TextField
					color="secondary"
					placeholder="First name"
					label="First name"
					helperText="Enter your first name"
					id="outlined-basic"
					variant="outlined"
					InputProps={{
						className: inputStyles.input,
					}}
				/>
				<TextField
					id="outlined-basic"
					variant="outlined"
					color="secondary"
					placeholder="Last name"
					helperText="Enter your last name"
					label="Last name"
				/>
				<TextField
					id="outlined-basic"
					variant="outlined"
					color="secondary"
					placeholder="Email address"
					helperText="Enter your email address"
					label="Email address"
				/>

				<FormControlLabel
					value="end"
					control={<Checkbox color="secondary" />}
					label="Please confirm that you are happy for us to send you emails in the future. You can view our privacy policy for more secondaryrmation"
					labelPlacement="end"
				/>
				<TextField
					id="outlined-basic"
					variant="outlined"
					color="secondary"
					placeholder="Password"
					helperText="Enter a password"
					label="Password"
					InputProps={{
						endAdornment: <SecurityIcon />,
					}}
				/>
				<TextField
					id="outlined-basic"
					variant="outlined"
					color="secondary"
					placeholder="Repeat password"
					helperText="Repeat password"
					label="Repeat password"
					InputProps={{
						endAdornment: <SecurityIcon />,
					}}
				/>
				<Box
					sx={{
						display: "flex",
						justifyContent: "flex-end",
					}}
				>
					<Button sx={{}} variant="contained" color="secondary">
						Register
						<ArrowForwardIosIcon />
					</Button>
				</Box>
			</CardContent>
		</Card>
	);
};

export default InputsTeacher;
