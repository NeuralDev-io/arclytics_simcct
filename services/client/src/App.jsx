/**
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this repository.
 *
 * App Component
 *
 * @version 1.2.0
 * @author Dalton Le, Arvy Salazar, Andrew Che
 *
 * This is the App Component which provides the React Router for the Arclytics
 * Sim React front-end client.
 *
 */

import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { SnackbarProvider } from 'notistack'
import { makeStyles } from '@material-ui/core/styles'
import store from './state/store'
import {
  PrivateRoute,
  AdminRoute,
  DemoRoute,
  ShareRoute,
} from './components/moleisms/routers'
import Toaster from './components/moleisms/toaster'
import FeedbackModal, { RatingModal } from './components/moleisms/feedback'
import ErrorBoundary from './components/pages/error-boundary/ErrorBoundary'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import NoMatchPage from './components/pages/no-match/NoMatchPage'
import SimulationPage from './components/pages/simulation'
import EquiPage from './components/pages/equi/EquiPage'
import AdminPage from './components/pages/admin'
import ProfileQuestionsPage from './components/pages/profile-questions'
import UserPage from './components/pages/user'
import UserSimulationPage from './components/pages/user-sim'
import UserAlloyPage from './components/pages/user-alloys'
import PasswordResetPage from './components/pages/password-reset'
import SharePage from './components/pages/share'
import Healthy from './components/moleisms/healthy/Healthy'
import AnalyticsPage from './components/pages/analytics'
import AboutPage from './components/pages/about/AboutPage'
/*
* DECISION:
* This was only use for testing of the ErrorBoundary and Logs so we will keep it here
* in case we may need to test some other errors in the future.
* */

// import TestRoute from './components/pages/test-route/TestRoute'
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
                render={(props) => <LoginPage {...props} />}
              />
              <Route
                path="/signup"
                render={(props) => <SignupPage {...props} />}
              />
              <PrivateRoute
                exact
                path="/"
                component={SimulationPage}
              />
              <PrivateRoute
                path="/equilibrium"
                component={EquiPage}
              />
              <PrivateRoute
                exact
                path="/user/simulations"
                component={UserSimulationPage}
              />
              <Route
                path="/about"
                component={AboutPage}
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
                path="/analytics"
                component={AnalyticsPage}
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
                render={(props) => <PasswordResetPage {...props} />}
              />

              {/*
                DECISION:
                This was only use for testing of the ErrorBoundary and Logs so we will keep it here
                in case we may need to test some other errors in the future.

                <Route
                  path="/test"
                  render={(props) => (<TestRoute {...props} />)}
                />

               */}

              <ShareRoute
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
