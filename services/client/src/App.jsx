import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import store from './state/store'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import SimulationPage from './components/pages/simulation'
import AdminPage from './components/pages/admin'
import ProfileQuestionsPage from './components/pages/profile-questions'
import UserPage from './components/pages/user'

import './App.scss'

function App() {
  return (
    <Provider store={store}>
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
          <Route
            exact
            path="/"
            render={props => <SimulationPage {...props} />}
          />
          <Route
            path="/profileQuestions"
            render={props => <ProfileQuestionsPage {...props}/>}
          />
          <Route
            path="/admin"
            render={props => <AdminPage {...props} />}
          />
          <Route
            path="/user"
            render={props => <UserPage {...props} />}
          />
        </Switch>
      </div>
    </Provider>
  )
}

export default App
