# Defining the class
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def search_bst(root, value):

    # Root is none or value is found
    if root is None:
        return False
    if root.value == value:
        return True
    
    # If value is smaller, search left, if larger, search right
    if value < root.value:
        return search_bst(root.left, value)
    else:
        return search_bst(root.right, value)


# Code Testing
if __name__ == "__main__":
    root = TreeNode(10)
    root.left = TreeNode(5)
    root.right = TreeNode(15)
    root.left.left = TreeNode(3)
    root.left.right = TreeNode(7)
    
    # Tests
    print(search_bst(root, 7))   # True
    print(search_bst(root, 15))  # True
    print(search_bst(root, 8))   # False

    # ChatGPT:
    #I would like to create a python function to search for a value in a binary search tree. The method should take the root of the tree and the value to be searched as parameters. It should return true if the value is found in the tree, and false if otherwise. Without giving me the code, what steps would I take to create this function?
    