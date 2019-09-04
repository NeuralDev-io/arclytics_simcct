import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch, Link } from 'react-router-dom'
import store from './state/store'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import SimulationPage from './components/pages/simulation'
import AdminPage from './components/pages/admin'
import ProfileQuestionsPage from './components/pages/profile-questions'
import ProfilePage from './components/moleisms/user-profile'
import UserSimulationPage from './components/pages/user-sim'
import UserAlloyPage from './components/pages/user-alloys'
import PasswordResetPage from './components/pages/password-reset'

import './App.scss'

function App() {
  return (
    <Provider store={store}>
      <div className="App">
        <Switch>
          {/* <Link to="/signin">Search</Link> */}
          <Route
            path="/signin:tokenexpired=:token"
            render={props => <LoginPage {...props} />}
          />
          <Route
            path="/signup"
            render={props => <SignupPage {...props} />}
          />
          <Route
            exact
            path="/"
            render={props => <SimulationPage {...props} />}
          />
          <Route
            exact
            path="/user/simulations"
            render={props => <UserSimulationPage {...props} />}
          />
          <Route
            exact
            path="/user/alloys"
            render={props => <UserAlloyPage {...props} />}
          />
          <Route
            path="/profileQuestions"
            render={props => <ProfileQuestionsPage {...props} />}
          />
          <Route
            path="/admin"
            render={props => <AdminPage {...props} />}
          />
          <Route
            path="/user/profile"
            render={props => <ProfilePage {...props} />}
          />
          <Route
            path="/password/reset=:token"
            render={props => <PasswordResetPage {...props} />}
          />
        </Switch>
      </div>
    </Provider>
  )
}

export default App
