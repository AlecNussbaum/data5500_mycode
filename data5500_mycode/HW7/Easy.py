# Defines class for nodes
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def insert_into_bst(root, value):
    # Creates new node if tree is empty
    if root is None:
        return TreeNode(value)

    # If not, keep going down tree
    if value < root.value:
        root.left = insert_into_bst(root.left, value)
    elif value > root.value:
        root.right = insert_into_bst(root.right, value)
    # If already exists, ignore

    return root


# code testing
if __name__ == "__main__":
    # Chosing values and testing them
    root = TreeNode(10)
    root = insert_into_bst(root, 5)
    root = insert_into_bst(root, 15)
    root = insert_into_bst(root, 7)

    def inorder(node):
        if node:
            inorder(node.left)
            print(node.value, end=" ")
            inorder(node.right)

    inorder(root)

    # ChatGPT Questions:
    # Can you explain simply to me the process of writing a Python function to insert a value into a binary search tree?
    # Can you look for errors in my code? The output is incorrect.
