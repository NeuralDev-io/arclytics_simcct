import React from 'react'
import { Provider } from 'react-redux'
import { Route, Switch } from 'react-router-dom'
import store from './state/store'
<<<<<<< HEAD
import LoginPage from './views/pages/LoginPage'
import SignupPage from './views/pages/signup/SignupPage'
=======
import LoginPage from './components/pages/LoginPage'
import SignupPage from './components/pages/SignupPage'
>>>>>>> develop

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
        </Switch>
      </div>
    </Provider>
  )
}

export default App
