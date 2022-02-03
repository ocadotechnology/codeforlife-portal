import { makeStyles } from "@mui/styles";

const variable = 30;

export const form = makeStyles({
  loginRegisterForm: {
    margin: `${variable / 2}vh 0 0 ${variable}vw`,
    width: "20%",
  },
  inputForm: {
    background: "rgb(224, 0, 77)",
    color: "white",
    padding: "1rem 2rem 1rem 2rem",
  },
  inputFormStudent: {
    background: "rgb(255, 190, 0)",
    color: "black",
    padding: "1rem 2rem 1rem 2rem",
  },
  tab: {
    width: "50%",
    "&:focus-within": {
      background: "rgba(224, 0, 77, 0.2)",
    },
  },
  textField: {
    width: "90%",
    marginLeft: "auto",
    marginRight: "auto",
    paddingBottom: 0,
    marginTop: 0,
    fontWeight: 500,
  },
  input: {
    color: "white",
  },
  inputStudent: {
    color: "black",
  },
});
