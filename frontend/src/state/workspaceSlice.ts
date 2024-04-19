import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit";
import { WorkspaceFile, getWorkspace } from "../services/fileService";
import { addNode, removeEmptyNodes } from "../components/file-explorer/utils";

type WorkspaceState = {
  workspace: WorkspaceFile;
  status: "idle" | "loading" | "succeeded" | "failed";
  error: string | null;
};

const initialState: WorkspaceState = {
  workspace: { name: "", children: [] },
  status: "idle",
  error: null,
};

export const fetchWorkspaceData = createAsyncThunk(
  "workspace/fetchWorkspaceData",
  async () => {
    const wsFile = await getWorkspace();
    return removeEmptyNodes(wsFile);
  },
);

const workspaceSlice = createSlice({
  name: "workspace",
  initialState,
  reducers: {
    addNodeToWorkspace: (state, action: PayloadAction<string>) => {
      const pathParts = action.payload.split("/");
      state.workspace = addNode([state.workspace], pathParts).pop()!;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWorkspaceData.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchWorkspaceData.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.workspace = action.payload;
      })
      .addCase(fetchWorkspaceData.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message || null;
      });
  },
});

export const { addNodeToWorkspace } = workspaceSlice.actions;

export default workspaceSlice.reducer;
