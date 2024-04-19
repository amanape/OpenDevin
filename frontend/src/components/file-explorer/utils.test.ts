import { addNode, removeEmptyNodes } from "./utils";

test("removeEmptyNodes removes empty arrays", () => {
  const tree = [
    {
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
    },
  ];

  expect(removeEmptyNodes(tree)).toEqual([
    {
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
    },
  ]);
});

describe("addNode", () => {
  it("should add a node to the tree", () => {
    const nodes = [
      {
        name: "a",
        children: [{ name: "b" }],
      },
    ];

    const pathParts = ["a", "c"];

    expect(addNode(nodes, pathParts)).toEqual([
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

    const deepNodes = [
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
                ],
              },
              {
                name: "e",
              },
            ],
          },
        ],
      },
    ];

    const pathParts2 = ["a", "b", "c", "f"];

    expect(addNode(deepNodes, pathParts2)).toEqual([
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
    const nodes = [
      {
        name: "a",
        children: [],
      },
    ];

    const pathParts = ["a", "b"];

    expect(addNode(nodes, pathParts)).toEqual([
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
