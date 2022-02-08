import { form } from "./LogInFormStyle";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import { Button, Checkbox, Typography } from "@mui/material";
import { FormControlLabel } from "@mui/material";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { TextField } from "@mui/material";
import SecurityIcon from "@mui/icons-material/Security";
import { Box } from "@mui/system";

const InputsIndepStudent = () => {
  const inputStyles = form();

  return (
    <Card className={inputStyles.inputFormStudent}>
      <CardContent>
        <Typography variant="h4">Independent learner</Typography>
        <Typography variant="subtitle2">
          Register below if you are not part of a school or club.
        </Typography>
        <Typography variant="caption">
          Are you part of a school or club? if so, plese log in here or speak to
          your teacher<br></br>
        </Typography>

        <TextField
          color="warning"
          placeholder="First name"
          label="First name"
          helperText="Enter your first name"
          id="outlined-basic"
          variant="outlined"
          InputProps={{
            className: inputStyles.inputStudent,
          }}
        />
        <TextField
          color="warning"
          placeholder="Username"
          label="Username"
          helperText="Enter your username"
          id="outlined-basic"
          variant="outlined"
          InputProps={{
            className: inputStyles.inputStudent,
          }}
        />
        <TextField
          color="warning"
          placeholder="Email address"
          label="Email address"
          helperText="Enter your email adress"
          id="outlined-basic"
          variant="outlined"
          InputProps={{
            className: inputStyles.inputStudent,
          }}
        />

        <FormControlLabel
          value="end"
          control={<Checkbox color="primary" />}
          label="Please confirm that you are happy for us to send you emails in the future. You can view our privacy policy for more primaryrmation"
          labelPlacement="end"
        />
        <TextField
          id="outlined-basic"
          variant="outlined"
          color="primary"
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
          color="primary"
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
          <Button
            variant="contained"
            color="inherit"
            endIcon={<ArrowForwardIosIcon />}
          >
            Register
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
};

export default InputsIndepStudent;
