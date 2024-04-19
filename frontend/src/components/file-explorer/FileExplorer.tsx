import React, { useCallback } from "react";
import {
  IoIosArrowBack,
  IoIosArrowForward,
  IoIosRefresh,
} from "react-icons/io";
import { twMerge } from "tailwind-merge";
import { useDispatch, useSelector } from "react-redux";
import ExplorerTree from "./ExplorerTree";
import IconButton from "../IconButton";
import { fetchWorkspaceData } from "../../state/workspaceSlice";
import { AppDispatch, RootState } from "../../store";

interface ExplorerActionsProps {
  onRefresh: () => void;
  toggleHidden: () => void;
  isHidden: boolean;
}

function ExplorerActions({
  toggleHidden,
  onRefresh,
  isHidden,
}: ExplorerActionsProps) {
  return (
    <div
      className={twMerge(
        "transform flex h-[24px] items-center gap-1 absolute top-4 right-2",
        isHidden ? "right-3" : "right-2",
      )}
    >
      {!isHidden && (
        <IconButton
          icon={
            <IoIosRefresh
              size={20}
              className="text-neutral-400 hover:text-neutral-100 transition"
            />
          }
          testId="refresh"
          ariaLabel="Refresh workspace"
          onClick={onRefresh}
        />
      )}

      <IconButton
        icon={
          isHidden ? (
            <IoIosArrowForward
              size={20}
              className="text-neutral-400 hover:text-neutral-100 transition"
            />
          ) : (
            <IoIosArrowBack
              size={20}
              className="text-neutral-400 hover:text-neutral-100 transition"
            />
          )
        }
        testId="close"
        ariaLabel="Close workspace"
        onClick={toggleHidden}
      />
    </div>
  );
}

interface FileExplorerProps {
  onFileClick: (path: string) => void;
}

function FileExplorer({ onFileClick }: FileExplorerProps) {
  const [isHidden, setIsHidden] = React.useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const workspace = useSelector(
    (state: RootState) => state.workspace.workspace,
  );

  const refreshWorkspace = useCallback(() => {
    dispatch(fetchWorkspaceData());
  }, [dispatch]);

  React.useEffect(() => {
    refreshWorkspace();
  }, [refreshWorkspace]);

  return (
    <div
      className={twMerge(
        "bg-neutral-800 h-full border-r-1 border-r-neutral-600 flex flex-col transition-all ease-soft-spring overflow-auto",
        isHidden ? "min-w-[48px]" : "min-w-[228px]",
      )}
    >
      <div className="flex p-2 items-center justify-between relative">
        <div style={{ display: isHidden ? "none" : "block" }}>
          <ExplorerTree
            tree={workspace}
            onFileClick={onFileClick}
            defaultOpen
          />
        </div>

        <ExplorerActions
          isHidden={isHidden}
          toggleHidden={() => setIsHidden((prev) => !prev)}
          onRefresh={refreshWorkspace}
        />
      </div>
    </div>
  );
}

export default FileExplorer;
