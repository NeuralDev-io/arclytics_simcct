import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { SnackbarProvider } from 'notistack'
import { makeStyles } from '@material-ui/core/styles'
import store from './state/store'
import { PrivateRoute, AdminRoute, DemoRoute } from './components/moleisms/routers'
import Toaster from './components/moleisms/toaster'
import FeedbackModal, { RatingModal } from './components/moleisms/feedback'
import ErrorBoundary from './components/pages/error-boundary/ErrorBoundary'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import NoMatchPage from './components/pages/no-match/NoMatchPage'
import TestRoute from './components/pages/test-route/TestRoute'// TODO(andrew@neuraldev.io): Delete this
import SimulationPage from './components/pages/simulation'
import AdminPage from './components/pages/admin'
import ProfileQuestionsPage from './components/pages/profile-questions'
import UserPage from './components/pages/user'
import UserSimulationPage from './components/pages/user-sim'
import UserAlloyPage from './components/pages/user-alloys'
import PasswordResetPage from './components/pages/password-reset'
import SharePage from './components/pages/share'
import Healthy from './components/moleisms/healthy/Healthy'

import './App.scss'

const useStyles = makeStyles({
  root: {
    zIndex: 9999,
  },
})

function App() {
  const classes = useStyles()

  return (
    <ErrorBoundary>
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
        classes={{
          root: classes.root,
        }}
      >
        <Provider store={store}>
          <Toaster />
          <div className="App">
            <FeedbackModal />
            <RatingModal />
            <Switch>
              <Route
                path="/healthy"
                Component={Healthy}
              />
              <Route
                path="/signin"
                render={props => <LoginPage {...props} />}
              />
              <Route
                path="/signup"
                render={props => <SignupPage {...props} />}
              />
              <PrivateRoute
                exact
                path="/"
                component={SimulationPage}
              />
              <PrivateRoute
                exact
                path="/user/simulations"
                component={UserSimulationPage}
              />
              <PrivateRoute
                exact
                path="/user/alloys"
                component={UserAlloyPage}
              />
              <PrivateRoute
                path="/profileQuestions"
                component={ProfileQuestionsPage}
              />
              <AdminRoute
                path="/admin"
                component={AdminPage}
              />
              <PrivateRoute
                path="/user"
                component={UserPage}
              />
              <Route
                path="/password/reset=:token"
                render={props => <PasswordResetPage {...props} />}
              />
              {/* TODO(andrew@neuraldev.io): DELETE THIS ROUTE - AFTER TESTING HTTP LOGGER */}
              <Route
                path="/test"
                render={props => (<TestRoute {...props} />)}
              />

              <DemoRoute
                path="/share/simulation/:token"
                component={SharePage}
              />
              <DemoRoute
                path="/demo"
                component={SimulationPage}
              />
              <Route component={NoMatchPage} />
            </Switch>
          </div>
        </Provider>
      </SnackbarProvider>
    </ErrorBoundary>
  )
}

export default App
