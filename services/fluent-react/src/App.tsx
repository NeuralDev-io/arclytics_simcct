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

import './App.css';

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

// style props passed from WithStyles<typeof styles> interface
interface Props extends WithStyles<typeof styles> {}

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

      /*
      * This method uses the fluent package plugin called in_http which exposes
      * an endpoint that will accept a log from the http source such as this
      * fetch request.
      *
      * Usage: URL --> http://host:port/tag.label
      * Body: {"container_name": string, "log": string, "source": string}
      * */
      httpLog(message: string, tag: string, label: string) {
        fetch(`http://localhost:9880/${tag}.${label}`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            container_name: '/arc_react_1',
            log: message,
            source: 'http'
          })
        })
            .then(response => console.log('Fluent http response: ', response))
            .catch(err => console.log(err));
      }

      handleSubmit = () => {
        const {message} = this.state
        console.log('message: ', message)

        // send an event record with using the in_http plugin from fluentd
        this.httpLog(message, 'fluent-react', 'debug')

        /*
        * This fetch call goes to the fluent-python container that contains an
        * endpoint which uses the Python fluent-logger to create en Event
        * that is emitted as a log to our fluent container.
        * */
        fetch('http://localhost:5005/log', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({'sender': 'Fluent-React-Typescript', 'message': message})
        })
            .then(response => response.json())
            .then(response => {
              console.log('Flask response: ', response)
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
