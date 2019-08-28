import React from 'react';
import logo from './logo.svg';
import {
  createStyles,
  Theme,
  WithStyles,
  withStyles,
  createMuiTheme
} from '@material-ui/core/styles';
import { ThemeProvider } from '@material-ui/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import Grid from "@material-ui/core/Grid";
import lightBlue from "@material-ui/core/colors/lightBlue";
// import blue from "@material-ui/core/colors/blue";

import './App.css';

const logger = require('fluent-logger')

logger.configure('fluent-react', {
  host: 'localhost',
  port: 24224,
  timeout: 3.0,
  reconnectInterval: 6000 // 1 minute
})

const appTheme = createMuiTheme({
  palette: {
    type: 'dark',
    primary: {
      // light: will be calculated from palette.primary.main,
      main: '#0076C2',
      // dark: will be calculated from palette.primary.main,
      // contrastText: will be calculated to contrast with palette.primary.main
    },
    secondary: lightBlue,
  },
});

const styles = (theme: Theme) => createStyles({
  root: {
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: theme.palette.background.default,
    color: theme.palette.primary.dark,
  },
  container: {
      display: 'flex',
      flexDirection: 'row',
  },
  textField: {
    marginLeft: theme.spacing(1),
    marginRight: theme.spacing(1),
    color: theme.palette.primary.light,
  },
  button: {
    margin: theme.spacing(1),
  },
});

interface Props extends WithStyles<typeof styles> {
  // style props passed from WithStyles<typeof styles> interface
}

interface IState {
  message?: string | any,
  response?: string | any,
}

const App = withStyles(styles)(
    class App extends React.Component<Props, IState> {
      constructor(props: Props) {
        super(props);
        this.state = {
          message: '',
          response: '',
        };

        this.onChange = this.onChange.bind(this);
      }

      onChange = (e: React.ChangeEvent<any>) => this.setState({message: e.target.value})

      handleSubmit = () => {
        const {message} = this.state
        console.log('message: ', message)
        // send an event record with 'tag.label'
        logger.emit('debug', {message: message, sender: 'fluent-react-typescript'});

        fetch('http://localhost:5005/log', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({'sender': 'Fluent-React-Typescript', 'message': message})
        })
            .then(response => response.json())
            .then(response => {
              console.log(response)
              this.setState({response: response.status})
            })
            .catch(err => console.log(err))
      }

      render() {
        const {response} = this.state;
        const {classes} = this.props

        return (
          <div className="App">
            <header className="App-header">
              <img src={logo} className="App-logo" alt="logo" />
              <Grid
                  container
                  direction="row"
                  justify="center"
                  alignItems="center"
              >
                <Grid item xs={12}>
                  <p>Arclytics Sim <code>fluentd</code> centralised logging test.</p>
                </Grid>
                <Grid item xs={4}>
                  <ThemeProvider theme={appTheme}>
                    <TextField
                        id="message"
                        label="Log Message"
                        rows="6"
                        className={classes.textField}
                        margin="normal"
                        variant="filled"
                        multiline
                        fullWidth
                        onChange={(event) => this.onChange(event)}
                    />
                  </ThemeProvider>
                </Grid>
                <Grid item xs={12}>
                  <ThemeProvider theme={appTheme}>
                    <Button
                        variant="contained"
                        color="primary"
                        className={classes.button}
                        onClick={this.handleSubmit}
                    >
                      LOG
                    </Button>
                  </ThemeProvider>
                </Grid>
                <Grid item xs={12}>
                  <h4>{response}</h4>
                </Grid>
              </Grid>
            </header>
          </div>
        );
      }
    }
);

export default App;
