import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import { SnackbarProvider } from 'notistack'
import store from './state/store'
import { PrivateRoute, AdminRoute, DemoRoute } from './components/moleisms/routers'
import Toaster from './components/moleisms/toaster'
import ErrorBoundary from './components/pages/error-boundary/ErrorBoundary'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import SimulationPage from './components/pages/simulation'
import AdminPage from './components/pages/admin'
import ProfileQuestionsPage from './components/pages/profile-questions'
import UserPage from './components/pages/user'
import UserSimulationPage from './components/pages/user-sim'
import UserAlloyPage from './components/pages/user-alloys'
import PasswordResetPage from './components/pages/password-reset'
import SharePage from './components/pages/share'

import './App.scss'

function App() {
  return (
    <ErrorBoundary>
      <SnackbarProvider
        maxSnack={3}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'center',
        }}
      >
        <Provider store={store}>
          <Toaster />
          <div className="App">
            <Switch>
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
              <DemoRoute
                path="/share/simulation/:token"
                component={SharePage}
              />
              <DemoRoute
                path="/demo"
                component={SimulationPage}
              />
            </Switch>
          </div>
        </Provider>
      </SnackbarProvider>
    </ErrorBoundary>
  )
}

export default App
