import {
  createStore, applyMiddleware, compose, combineReducers,
} from 'redux'
import thunk from 'redux-thunk'
import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage'
import * as reducers from './ducks'
import userPersistReducer from './ducks/user-persist/reducers'

const persistConfig = {
  key: 'userPersist',
  storage,
}

const rootReducer = combineReducers({
  ...reducers,
  user: persistReducer(persistConfig, userPersistReducer),
})

const initialState = {}

const middleware = [thunk]

const store = createStore(
  rootReducer,
  initialState,
  compose(
    applyMiddleware(...middleware),
    // eslint-disable-next-line no-underscore-dangle
    (window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()) || compose,
  ),
)

export const persistor = persistStore(store)

export default store