import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import store from './state/store'
import LoginPage from './components/pages/login/LoginPage'
import SignupPage from './components/pages/signup/SignupPage'
import SimulationPage from './components/pages/simulation'

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
        </Switch>
      </div>
    </Provider>
  )
}

export default App
