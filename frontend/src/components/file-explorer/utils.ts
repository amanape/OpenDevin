export const removeEmptyNodes = (tree: TreeNode[]): TreeNode[] =>
  tree.map((node) => {
    if (node.children) {
      const children = removeEmptyNodes(node.children);
      return {
        ...node,
        children: children.length ? children : undefined,
      };
    }
    return node;
  });

/**
 * Recursive function to add a node to a tree structure.
 *
 * @param nodes - The current list of nodes in the tree.
 * @param pathParts - The parts of the path to the new node.
 * @returns The updated list of nodes.
 */
export const addNode = (nodes: TreeNode[], pathParts: string[]): TreeNode[] => {
  // If there are no more parts in the path, return the current nodes.
  if (pathParts.length === 0) {
    return nodes;
  }

  // Split the path into the current part (head) and the remaining parts (tail).
  const [head, ...tail] = pathParts;

  // Try to find an existing node with the same name as the current part.
  let node = nodes.find((n) => n.name === head);

  // If no such node exists, create a new one and add it to the list of nodes.
  if (!node) {
    node = { name: head };
    nodes.push(node);
  }

  // If there are more parts in the path, add them as children of the current node.
  // If the current node doesn't have any children yet, initialize it with an empty array.
  if (tail.length > 0) {
    node.children = addNode(node.children || [], tail);
  }

  // Return the updated list of nodes.
  return nodes;
};
