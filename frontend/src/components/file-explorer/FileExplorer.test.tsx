import React from "react";
import { waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { act } from "react-dom/test-utils";
import FileExplorer from "./FileExplorer";
import { getWorkspace } from "../../services/fileService";
import { renderWithProviders } from "../../../test-utils";

vi.mock("../../services/fileService", async () => ({
  getWorkspace: vi.fn(async () => ({
    name: "root",
    children: [
      { name: "file1.ts" },
      { name: "folder1", children: [{ name: "file2.ts" }] },
    ],
  })),

  selectFile: vi.fn(async (file: string) => file),
}));

describe("FileExplorer", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("should get the workspace directory", async () => {
    const { getByText } = renderWithProviders(
      <FileExplorer onFileClick={vi.fn} />,
    );

    expect(getWorkspace).toHaveBeenCalledTimes(1);
    await waitFor(() => {
      expect(getByText("root")).toBeInTheDocument();
    });
  });

  it.todo("should render an empty workspace if the workspace is empty");

  it.todo("should render a loading spinner while fetching the workspace");

  it("calls the onFileClick function when a file is clicked", async () => {
    const onFileClickMock = vi.fn();
    const { getByText } = renderWithProviders(
      <FileExplorer onFileClick={onFileClickMock} />,
    );

    await waitFor(() => {
      expect(getByText("folder1")).toBeInTheDocument();
    });

    act(() => {
      userEvent.click(getByText("folder1"));
    });

    act(() => {
      userEvent.click(getByText("file2.ts"));
    });

    const absPath = "root/folder1/file2.ts";
    expect(onFileClickMock).toHaveBeenCalledWith(absPath);
  });

  it("should refetch the workspace when clicking the refresh button", () => {
    const { getByTestId } = renderWithProviders(
      <FileExplorer onFileClick={vi.fn} />,
    );

    act(() => {
      userEvent.click(getByTestId("refresh"));
    });

    expect(getWorkspace).toHaveBeenCalledTimes(2); // 1 from initial render, 1 from refresh button
  });

  it("should toggle the explorer visibility when clicking the close button", async () => {
    const { getByTestId, getByText, queryByText } = renderWithProviders(
      <FileExplorer onFileClick={vi.fn} />,
    );

    await waitFor(() => {
      expect(getByText("root")).toBeInTheDocument();
    });

    act(() => {
      userEvent.click(getByTestId("close"));
    });

    // it should be hidden rather than removed from the DOM
    expect(queryByText("root")).toBeInTheDocument();
    expect(queryByText("root")).not.toBeVisible();
  });
});
