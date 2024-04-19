import { combineReducers, configureStore } from "@reduxjs/toolkit";
import browserReducer from "./state/browserSlice";
import chatReducer from "./state/chatSlice";
import codeReducer from "./state/codeSlice";
import workspaceReducer from "./state/workspaceSlice";
import commandReducer from "./state/commandSlice";
import taskReducer from "./state/taskSlice";
import errorsReducer from "./state/errorsSlice";
import settingsReducer from "./state/settingsSlice";
import agentReducer from "./state/agentSlice";

export const rootReducer = combineReducers({
  browser: browserReducer,
  chat: chatReducer,
  code: codeReducer,
  workspace: workspaceReducer,
  cmd: commandReducer,
  task: taskReducer,
  errors: errorsReducer,
  settings: settingsReducer,
  agent: agentReducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export type RootState = ReturnType<typeof store.getState>;
export type AppStore = typeof store;
export type AppDispatch = typeof store.dispatch;

export default store;
