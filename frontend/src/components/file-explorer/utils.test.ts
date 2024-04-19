import { addNode, removeEmptyNodes } from "./utils";

describe("addNode", () => {
  it("should add a node to the tree", () => {
    const root = {
      name: "a",
      children: [{ name: "b" }],
    };

    const pathParts = ["a", "c"];

    expect(addNode([root], pathParts)).toEqual([
      {
        name: "a",
        children: [
          {
            name: "b",
          },
          {
            name: "c",
          },
        ],
      },
    ]);

    const deepNodes = {
      name: "a",
      children: [
        {
          name: "b",
          children: [
            {
              name: "c",
              children: [
                {
                  name: "d",
                },
              ],
            },
            {
              name: "e",
            },
          ],
        },
      ],
    };

    const pathParts2 = ["a", "b", "c", "f"];

    expect(addNode([deepNodes], pathParts2)).toEqual([
      {
        name: "a",
        children: [
          {
            name: "b",
            children: [
              {
                name: "c",
                children: [
                  {
                    name: "d",
                  },
                  {
                    name: "f",
                  },
                ],
              },
              {
                name: "e",
              },
            ],
          },
        ],
      },
    ]);
  });

  it("should add a node to an empty children array", () => {
    const root = {
      name: "a",
      children: [],
    };

    const pathParts = ["a", "b"];

    expect(addNode([root], pathParts)).toEqual([
      {
        name: "a",
        children: [
          {
            name: "b",
          },
        ],
      },
    ]);
  });
});

test("removeEmptyNodes removes empty arrays", () => {
  const root = {
    name: "a",
    children: [
      {
        name: "b",
        children: [],
      },
      {
        name: "c",
        children: [
          {
            name: "d",
            children: [],
          },
        ],
      },
    ],
  };

  expect(removeEmptyNodes(root)).toEqual({
    name: "a",
    children: [
      {
        name: "b",
      },
      {
        name: "c",
        children: [
          {
            name: "d",
          },
        ],
      },
    ],
  });
});
