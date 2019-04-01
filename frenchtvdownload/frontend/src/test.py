data = ["hello", "how", "are", "you", "today", "yourself", "todo"]

class TreeNode:
  class node:
    def __init__(self, l)
      self.letter = l
      self.child = []

  def __init__(self):  
    self.root = self.node()
  
  def add(self, word):
    currentNode = self.root
    for letter in word:
        found = False
        for child in currentNode.child:
            if child.letter == letter:
                currentNode = child
                found = True
                break 
                
        if (not found):
          newNode = TreeNode(letter, [])
          currentNode.child.append(newNode)
          currentNode = newNode

  def print(self, root, )
    if len(root.child):
      self.printlenchild.length == letter:
        currentNode = child
        found = True
        break 




tree = TreeNode()

for word in data:
  currentNode = tree
  for letter in word:
      found = False
      for child in currentNode.child:
          if child.letter == letter:
              currentNode = child
              found = True
              break 
              
      if (not found):
        newNode = TreeNode(letter, [])
        currentNode.child.append(newNode)
        currentNode = newNode

s